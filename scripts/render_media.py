"""Render CAD illustrations and a verified cube solve without opening a serial port.

Run from any directory: python scripts/render_media.py
Requires scripts/requirements-media.txt. Geometry is rasterized locally; no AI
images, tutorial photographs, or downloaded model assets are used.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import io
import json
import math
from pathlib import Path
import struct
import types

import kociemba
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'images'
COLORS = {
    'b': '#368ee8', 'r': '#eb535a', 'g': '#2cbd8c',
    'o': '#fb9349', 'w': '#ecf2f8', 'y': '#ffd35b',
}
SIDES = ['L', 'F', 'R', 'B', 'D', 'U']
AXES = {
    'R': np.array([1., 0, 0]), 'L': np.array([-1., 0, 0]),
    'U': np.array([0., 1, 0]), 'D': np.array([0., -1, 0]),
    'F': np.array([0., 0, 1]), 'B': np.array([0., 0, -1]),
}


def rgb(color):
    return np.array(tuple(bytes.fromhex(color.lstrip('#'))), dtype=float)


def font(size, bold=False, mono=False):
    stem = 'DejaVuSansMono' if mono else 'DejaVuSans'
    name = stem + ('-Bold' if bold else '') + '.ttf'
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size=size)


def background(width, height):
    y, x = np.mgrid[:height, :width]
    glow = np.exp(-((x - width * .7) ** 2 + (y - height * .4) ** 2)
                  / (width * .5) ** 2)
    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    for axis, (base, amplitude) in enumerate([(12, 9), (20, 18), (32, 25)]):
        pixels[:, :, axis] = base + amplitude * glow
    return Image.fromarray(pixels)


def rotation(axis, angle):
    axis = np.asarray(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    x, y, z = axis
    cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return (np.eye(3) * math.cos(angle) + cross * math.sin(angle)
            + np.outer(axis, axis) * (1 - math.cos(angle)))


def box(center, dimensions, color, matrix=None):
    center, dimensions = np.array(center), np.array(dimensions)
    vertices = np.array([[x, y, z] for x in [-.5, .5]
                         for y in [-.5, .5] for z in [-.5, .5]]) * dimensions
    if matrix is not None:
        vertices = vertices @ matrix.T
    vertices += center
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [(vertices[list(face)], color) for face in faces]


def stl(name, color, matrix=None, offset=(0, 0, 0)):
    data = (ROOT / 'STL_files' / name).read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError(f'Expected a binary STL: {name}')
    result = []
    for i in range(count):
        vertices = np.array(struct.unpack_from('<9f', data, 96 + i * 50)).reshape(3, 3)
        if matrix is not None:
            vertices = vertices @ matrix.T
        result.append((vertices + offset, color))
    return result


def rasterize(image, polygons, center, scale, camera=(7, 5, 9)):
    """Orthographic triangle rasterization with a depth buffer and studio lighting."""
    camera = np.array(camera, dtype=float)
    camera /= np.linalg.norm(camera)
    right = np.cross([0., 1, 0], camera)
    right /= np.linalg.norm(right)
    up = np.cross(camera, right)
    basis = np.stack([right, -up, camera])
    light = np.array([-3., 7, 6])
    light /= np.linalg.norm(light)
    pixels = np.array(image).copy()
    depth = np.full((image.height, image.width), -np.inf)
    for vertices, color in polygons:
        normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
        length = np.linalg.norm(normal)
        if length < 1e-8:
            continue
        normal /= length
        # Some third-party meshes use mixed winding. Shade both sides consistently.
        if np.dot(normal, camera) < 0:
            normal = -normal
        projected = vertices @ basis.T
        projected[:, :2] = projected[:, :2] * scale + np.array(center)
        shade = .48 + .48 * max(0, np.dot(normal, light))
        color_rgb = np.clip(rgb(color) * shade + 6, 0, 255).astype(np.uint8)
        for index in range(1, len(projected) - 1):
            triangle = projected[[0, index, index + 1]]
            low = np.maximum(np.floor(triangle[:, :2].min(0)).astype(int), [0, 0])
            high = np.minimum(np.ceil(triangle[:, :2].max(0)).astype(int),
                              [image.width - 1, image.height - 1])
            if np.any(low > high):
                continue
            a, b, c = triangle
            determinant = ((b[1] - c[1]) * (a[0] - c[0])
                           + (c[0] - b[0]) * (a[1] - c[1]))
            if abs(determinant) < 1e-8:
                continue
            yy, xx = np.mgrid[low[1]:high[1]+1, low[0]:high[0]+1]
            aa = ((b[1]-c[1])*(xx-c[0]) + (c[0]-b[0])*(yy-c[1])) / determinant
            bb = ((c[1]-a[1])*(xx-c[0]) + (a[0]-c[0])*(yy-c[1])) / determinant
            cc = 1 - aa - bb
            zz = aa*a[2] + bb*b[2] + cc*c[2]
            region = np.s_[low[1]:high[1]+1, low[0]:high[0]+1]
            mask = ((aa >= -1e-6) & (bb >= -1e-6) & (cc >= -1e-6)
                    & (zz > depth[region]))
            depth[region][mask] = zz[mask]
            pixels[region][mask] = color_rgb
    return Image.fromarray(pixels)


def cube_mesh(state, center=(0, 0, 0), size=1, turn=None, progress=0):
    polygons = []
    normal = AXES[turn[0]] if turn else None
    angle = (-1 if not turn or "'" not in turn else 1) * math.pi / 2
    if turn and '2' in turn:
        angle *= 2
    matrix = rotation(normal, angle * progress) if turn else np.eye(3)

    def transform(points, layer_position):
        if turn and np.dot(layer_position, normal) > .5:
            points = points @ matrix.T
        return points * size + center

    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                cubie = np.array([x, y, z])
                for vertices, color in box(cubie, [.965] * 3, '#182331'):
                    polygons.append((transform(vertices, cubie), color))
    for side, face in enumerate(SIDES):
        for row in range(3):
            for col in range(3):
                if face == 'F':
                    p, u, v = [col-1, 1-row, 1.49], [1, 0, 0], [0, -1, 0]
                elif face == 'B':
                    p, u, v = [1-col, 1-row, -1.49], [-1, 0, 0], [0, -1, 0]
                elif face == 'R':
                    p, u, v = [1.49, 1-row, 1-col], [0, 0, -1], [0, -1, 0]
                elif face == 'L':
                    p, u, v = [-1.49, 1-row, col-1], [0, 0, 1], [0, -1, 0]
                elif face == 'U':
                    p, u, v = [col-1, 1.49, row-1], [1, 0, 0], [0, 0, 1]
                else:
                    p, u, v = [col-1, -1.49, 1-row], [1, 0, 0], [0, 0, -1]
                p, u, v = np.array(p), np.array(u), np.array(v)
                # Eight corners soften the sticker edges without an image texture.
                corners = [(-.37, -.44), (.37, -.44), (.44, -.37), (.44, .37),
                           (.37, .44), (-.37, .44), (-.44, .37), (-.44, -.37)]
                vertices = np.array([p + a*u + b*v for a, b in corners])
                polygons.append((transform(vertices, np.round(p)), COLORS[state[side][row][col]]))
    return polygons


def load_cube_class():
    """Load the actual model class without importing motor.py or starting Pygame."""
    tree = ast.parse((ROOT / 'rubics_cube.py').read_text())
    node = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    names = ['up', 'down', 'left', 'right', 'front', 'back']
    motor = types.SimpleNamespace(**{name + suffix: lambda: None
                                    for name in names for suffix in ['', '_prime']})
    scope = {'motor': motor}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'rubics_cube.py', 'exec'), scope)
    cls = scope['rubics_cube']
    cube = cls.__new__(cls)
    cube.render_cube = lambda: None
    cube.char_cube = [[[color] * 3 for _ in range(3)] for color in ['b', 'r', 'g', 'o', 'w', 'y']]
    return cube


def apply(cube, move):
    name = {'U': 'up', 'D': 'down', 'L': 'left', 'R': 'right', 'F': 'front', 'B': 'back'}[move[0]]
    if "'" in move:
        name += '_prime'
    for _ in range(2 if '2' in move else 1):
        with contextlib.redirect_stdout(io.StringIO()):
            getattr(cube, name)()


def verified_solve():
    cube = load_cube_class()
    scramble = "R U F2 L D' B R2 U' F L2 D B2".split()
    for move in scramble:
        apply(cube, move)
    color_to_face = dict(zip('ygrwbo', 'URFDLB'))
    definition = ''.join(color_to_face[c] for side in [5, 2, 1, 4, 0, 3]
                         for row in cube.char_cube[side] for c in row)
    solution = kociemba.solve(definition).split()
    states = [copy.deepcopy(cube.char_cube)]
    for move in solution:
        apply(cube, move)
        states.append(copy.deepcopy(cube.char_cube))
    with contextlib.redirect_stdout(io.StringIO()):
        assert cube.is_cube_solved(), 'Rendered sequence must end in a solved cube'
    metadata = {'scramble': ' '.join(scramble), 'facelets_URFDLB': definition,
                'solution': ' '.join(solution), 'face_turns': len(solution),
                'verified_solved': True,
                'note': 'Software simulation; animation timing is illustrative.'}
    (OUT / 'solve-sequence.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return states, solution


def shadow(image, bounds):
    overlay = Image.new('RGBA', image.size)
    ImageDraw.Draw(overlay).ellipse(bounds, fill=(0, 0, 0, 150))
    overlay = overlay.filter(ImageFilter.GaussianBlur(24))
    return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')


def motor_mesh(center, axis):
    # Generic illustrative motor, not a claim about the project's exact model.
    axis = np.array(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    source = np.array([0., 0, 1])
    if np.allclose(axis, -source):
        matrix = rotation([0., 1, 0], math.pi)
    elif np.allclose(axis, source):
        matrix = np.eye(3)
    else:
        matrix = rotation(np.cross(source, axis), math.acos(np.dot(source, axis)))
    center = np.array(center)
    polygons = box(center, [42, 42, 32], '#394655', matrix)
    for offset in [-17, 17]:
        polygons += box(center + axis*offset, [42, 42, 3], '#aebac7', matrix)
    polygons += box(center + axis*28, [5, 5, 22], '#cbd5df', matrix)
    return polygons


def hero(state):
    image = background(1600, 900)
    image = shadow(image, (710, 650, 1490, 810))
    polygons = stl('base_plate.stl', '#2d829b')
    # Inferred concept layout: use actual meshes, showing the top access open.
    for i in range(4):
        matrix = rotation([0., 1, 0], i*math.pi/2)
        offset = np.array([0, 49, 61]) @ matrix.T
        name = 'stepper_motor_mount_' + ('a' if i % 2 == 0 else 'b') + '+(x2).stl'
        polygons += stl(name, '#3a9db1', matrix, offset)
        motor_center = np.array([0, 104, 67]) @ matrix.T
        axis = np.array([0, 0, -1]) @ matrix.T
        polygons += motor_mesh(motor_center, axis)
    polygons += motor_mesh([0, 34, 0], [0, 1, 0])
    polygons += cube_mesh(state, np.array([0., 104, 0]), 18)
    image = rasterize(image, polygons, (1150, 690), 3.25, camera=(8, 6, 10))
    draw = ImageDraw.Draw(image)
    draw.text((78, 75), 'A BROTHERS’ BUILD  /  2024', font=font(18, mono=True), fill='#6fd4da')
    draw.text((72, 160), 'Rubik’s cube', font=font(76, True), fill='#f1f5fa')
    draw.text((72, 248), 'robot.', font=font(102, True), fill='#f1f5fa')
    draw.text((78, 404), 'Five driven faces.', font=font(32), fill='#b4c8d8')
    draw.text((78, 451), 'One clever workaround.', font=font(32), fill='#b4c8d8')
    draw.line((80, 543, 500, 543), fill='#31465a', width=2)
    draw.text((78, 577), 'PYTHON  →  SERIAL  →  ARDUINO', font=font(19, mono=True), fill='#76d4db')
    draw.text((78, 620), 'Kociemba solving · stepper control', font=font(21), fill='#9bafc2')
    draw.rounded_rectangle((78, 748, 341, 792), radius=22, fill='#243c4c')
    draw.text((98, 758), 'ILLUSTRATIVE CAD RENDER', font=font(14, mono=True), fill='#bbdce6')
    draw.text((78, 838), 'Existing printed-part meshes · inferred assembly · generic motor bodies',
              font=font(16), fill='#8c9eb2')
    image.save(OUT / 'robot-concept.png', optimize=True)


def parts_gallery():
    image = background(1600, 1050)
    draw = ImageDraw.Draw(image)
    draw.text((62, 40), 'The printed structure', font=font(48, True), fill='#edf4fa')
    draw.text((65, 107), 'CAD STUDY  /  SIX EXISTING MESHES FROM STL_files',
              font=font(17, mono=True), fill='#74d0d7')
    entries = [
        ('base_plate.stl', '01  Base plate', '#4aa6b4'),
        ('stepper_motor_mount_a+(x2).stl', '02  Motor mount A', '#65b7bc'),
        ('stepper_motor_mount_b+(x2).stl', '03  Motor mount B', '#4ba0b9'),
        ('top_stepper_motor_mount.stl', '04  Top motor mount', '#5ba7bd'),
        ('brace+(x4).stl', '05  Corner brace', '#74bbc3'),
        ('cube_adapter_a+(x4).stl', '06  Cube adapter A', '#7bc5c8'),
    ]
    for i, (name, title, color) in enumerate(entries):
        col, row = i % 3, i // 3
        left, top = 58 + col*506, 175 + row*405
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((left, top, left+475, top+375), radius=18,
                               fill='#162636', outline='#2a4154', width=1)
        polygons = stl(name, color)
        vertices = np.concatenate([v for v, _ in polygons])
        middle = (vertices.min(0) + vertices.max(0)) / 2
        polygons = [(v-middle, c) for v, c in polygons]
        camera = np.array([7., 6, 10]); camera /= np.linalg.norm(camera)
        right = np.cross([0., 1, 0], camera); right /= np.linalg.norm(right)
        up = np.cross(camera, right)
        projected = (vertices-middle) @ np.stack([right, up]).T
        extent = np.ptp(projected, axis=0)
        scale = min(375/extent[0], 255/extent[1])
        image = rasterize(image, polygons, (left+237, top+160), scale, camera)
        draw = ImageDraw.Draw(image)
        draw.text((left+23, top+319), title, font=font(21, True), fill='#e3edf5')
    ImageDraw.Draw(image).text((64, 1008), 'Third-party mechanical design · see README credits · colors are illustrative',
                               font=font(16), fill='#9aafc1')
    image.save(OUT / 'cad-parts.png', optimize=True)


def solve_animation(states, solution):
    width, height = 1000, 660
    base = shadow(background(width, height), (450, 482, 930, 598))
    frames, durations = [], []

    def frame(state, index, move=None, progress=0):
        image = rasterize(base, cube_mesh(state, turn=move, progress=progress),
                          (700, 325), 103, camera=(7, 5, 9))
        draw = ImageDraw.Draw(image)
        draw.text((43, 42), 'SOLVE / SIMULATION', font=font(15, mono=True), fill='#71cfd7')
        draw.text((40, 111), 'From scramble', font=font(33, True), fill='#ecf3fa')
        draw.text((40, 153), 'to solved.', font=font(43, True), fill='#ecf3fa')
        draw.text((43, 239), 'Kociemba’s two-phase solver', font=font(17), fill='#b5c8d9')
        draw.text((43, 270), 'Verified with this repo’s cube model', font=font(15), fill='#94aabe')
        draw.text((43, 359), f'{index:02d} / {len(solution):02d}', font=font(37, mono=True), fill='#79d3db')
        label = 'SOLVED' if index == len(solution) else f'MOVE  {move or solution[0]}'
        draw.text((43, 421), label, font=font(27, True), fill='#eff4f9')
        draw.rounded_rectangle((44, 494, 356, 500), radius=3, fill='#2b3e50')
        if index:
            draw.rounded_rectangle((44, 494, 44+312*index/len(solution), 500), radius=3, fill='#66cbd0')
        draw.text((43, 588), 'SOFTWARE ANIMATION · ILLUSTRATIVE TIMING',
                  font=font(12, mono=True), fill='#8ea6ba')
        return image

    frames.append(frame(states[0], 0)); durations.append(900)
    for index, move in enumerate(solution):
        for step in range(1, 9):
            t = step / 8
            eased = t*t*(3-2*t)
            frames.append(frame(states[index], index, move, eased)); durations.append(70)
        frames.append(frame(states[index+1], index+1,
                            solution[index+1] if index+1 < len(solution) else None))
        durations.append(160)
    frames[-1].save(OUT / 'solved-preview.png', optimize=True)
    durations[-1] = 2400
    # A shared palette prevents color flicker between frames.
    palette = frames[0].quantize(colors=160)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(OUT / 'solve-simulation.gif', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    states, solution = verified_solve()
    hero(states[0])
    print('Rendered robot concept', flush=True)
    parts_gallery()
    print('Rendered CAD parts', flush=True)
    solve_animation(states, solution)
    print('Rendered verified solve:', ' '.join(solution), flush=True)


if __name__ == '__main__':
    main()
