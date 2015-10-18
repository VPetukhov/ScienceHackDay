from functools import reduce
import math
import bpy


class Point:
	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z


def read_mesh(filename):
	vertices = []
	faces = []
	normals = []

	with open(filename) as file:
		for row in file:
			(type, x, y, z) = row.split()
			if type == 'f':
				faces.append((int(x), int(y), int(z)))
			else:
				vert = Point()
				vert.x = float(x)
				vert.y = float(y)
				vert.z = float(z)
				vertices.append(vert)

	for face in faces:
		normals.append(get_normal(vertices[face[0] - 1], vertices[face[1] - 1], vertices[face[2] - 1]))

	vert_normals = [Point() for _ in vertices]

	for i in range(len(faces)):
		vert0 = vert_normals[faces[i][0] - 1]
		vert1 = vert_normals[faces[i][1] - 1]
		vert2 = vert_normals[faces[i][2] - 1]

		vert0.x += normals[i].x
		vert1.x += normals[i].x
		vert2.x += normals[i].x

		vert0.y += normals[i].y
		vert1.y += normals[i].y
		vert2.y += normals[i].y

		vert0.z += normals[i].z
		vert1.z += normals[i].z
		vert2.z += normals[i].z

	# for i in range(len(vertices)):
	# 	norm = vert_normals[i]
	# 	norm.x *= -1
	# 	norm.y *= -1
	# 	norm.z *= -1

	return vertices, faces, vert_normals


def print_mesh(vertices, faces, normals, filename):
	with open(filename, 'w') as file:
		for v in vertices:
			file.write('v %f %f %f\n' % (v.x, v.y, v.z))

		for f in faces:
			file.write('f %d//%d %d//%d %d//%d\n' % (f[0], f[0], f[1], f[1], f[2], f[2]))

		for n in normals:
			file.write('vn %f %f %f\n' % (n.x, n.y, n.z))


def read_mask(filename):
	with open(filename) as file:
		return list(list([float(c) for c in row.split()]) for row in file)


def get_scaling(vertices, mask):
	min_x = min([v.x for v in vertices])
	max_x = max([v.x for v in vertices])

	min_y = min([v.y for v in vertices])
	max_y = max([v.y for v in vertices])

	x_scale = len(mask[0]) / (max_x - min_x)
	x_disp = int((0 - min_x) * x_scale)

	y_scale = len(mask) / (max_y - min_y)
	y_disp = int((0 - min_y) * y_scale)

	return x_scale, x_disp, y_scale, y_disp


def displace_mask_vertices(mask, vertices, mult):
	(x_scale, x_disp, y_scale, y_disp) = get_scaling(vertices, mask)

	for vert in vertices:
		x = int(vert.x * x_scale) + x_disp
		y = int(vert.y * y_scale) + y_disp

		mask_val = mask[len(mask) - y - 1][x]
		if (mask_val == -1):
			# vert.z = 0
			continue
		else:
			vert.z += mult * mask_val
			# vert.z = mult * ( mask[len(mask) - y - 1][x])


def get_face_space(verts, face):
	a = get_length(verts[face[0] - 1].x - verts[face[1] - 1].x, verts[face[0] - 1].x - verts[face[1] - 1].x, verts[face[0] - 1].x - verts[face[1] - 1].x)
	b = get_length(verts[face[0] - 1].x - verts[face[2] - 1].x, verts[face[0] - 1].x - verts[face[2] - 1].x, verts[face[0 - 1]].x - verts[face[2] - 1].x)
	c = get_length(verts[face[1] - 1].x - verts[face[2] - 1].x, verts[face[1] - 1].x - verts[face[2] - 1].x, verts[face[1] - 1].x - verts[face[2] - 1].x)
	p = a + b + c
	return math.sqrt(p * (p - a) * (p - b) * (p - c))


def get_area_mask_vertices(mask, vertices, faces, mult):
	(x_scale, x_disp, y_scale, y_disp) = get_scaling(vertices, mask)

	# res_verts = [Point(p.x, p.y, p.z) for p in vertices]
	res_verts = [Point() for _ in vertices]

	for face in faces:
		mid = get_face_mid(vertices, face)

		x = int(mid.x * x_scale) + x_disp
		y = int(mid.y * y_scale) + y_disp

		mask_val = mask[len(mask) - y - 1][x]
		if (mask_val == -1):
			# mask_val = -1000
			continue

		for i in face:
			res_verts[i - 1].x += (vertices[i - 1].x - mid.x) * mask_val
			res_verts[i - 1].y += (vertices[i - 1].y - mid.y) * mask_val
			res_verts[i - 1].z += (vertices[i - 1].z - mid.z) * mask_val

	for i, vert in enumerate(res_verts):
		vert.x = vert.x * mult / 3 + vertices[i].x
		vert.y = vert.y * mult / 3 + vertices[i].y
		vert.z = vert.z * mult / 3 + vertices[i].z

	res_faces = []
	for face in faces:
		if (get_face_space(res_verts, face) / get_face_space(vertices, face) > 1.5):
			rv_mid = get_face_mid(res_verts, face)
			norm = get_normal(res_verts[face[0]], res_verts[face[1]], res_verts[face[2]])
			# norm.x *= -1; norm.y *= -1; norm.z *= -1;
			last_ind = len(res_verts)
			norm_mult = 0.001
			res_verts.append(Point(rv_mid.x + norm.x * norm_mult, rv_mid.y + norm.y * norm_mult, rv_mid.z + norm.z * norm_mult))
			# res_verts.append(rv_mid)
			res_faces.append((face[0], face[1], last_ind + 1))
			res_faces.append((face[0], last_ind + 1, face[2]))
			res_faces.append((face[1], face[2], last_ind + 1))
		else:
			res_faces.append(face)

	return res_verts, res_faces


def get_face_mid(vertices, face):
	mid = Point(
		(vertices[face[0] - 1].x + vertices[face[1] - 1].x + vertices[face[2] - 1].x) / 3,
		(vertices[face[0] - 1].y + vertices[face[1] - 1].y + vertices[face[2] - 1].y) / 3,
		(vertices[face[0] - 1].z + vertices[face[1] - 1].z + vertices[face[2] - 1].z) / 3
	)
	return mid


def get_length(x, y, z):
	return math.sqrt(x ** 2 + y ** 2 + z ** 2)


def get_normal(p1, p2, p3):
	assert isinstance(p1, Point)
	assert isinstance(p2, Point)
	assert isinstance(p3, Point)

	res = Point()
	res.x = p1.y*(p2.z - p3.z) + p2.y * (p3.z - p1.z) + p3.y * (p1.z - p2.z)
	res.y = p1.z*(p2.x - p3.x) + p2.z * (p3.x - p1.x) + p3.z * (p1.x - p2.x)
	res.z = p1.x*(p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)

	normalizer = get_length(res.x, res.y, res.z)
	res.x /= normalizer
	res.y /= normalizer
	res.z /= normalizer

	return res


def run_displace(filename):
	(vertices, faces, normals) = read_mesh('/Work/SHD/ScienceHackDay/Data/model.txt')
	mask = read_mask(filename + '.txt')
	displace_mask_vertices(mask, vertices, 0.03)
	# print_mesh(vertices, faces, normals, '/Work/SHD/ScienceHackDay/project/faceapp/static/faceapp/models/base.obj')
	print_mesh(vertices, faces, normals, '/Work/SHD/ScienceHackDay/project/faceapp/static/faceapp/models/' + filename + '.obj')


def run_area(filename):
	(vertices, faces, normals) = read_mesh('/Work/SHD/ScienceHackDay/Data/model.txt')
	mask = read_mask(filename + '.txt')
	vertices, faces = get_area_mask_vertices(mask, vertices, faces, 5)
	print_mesh(vertices, faces, normals, '/Work/SHD/ScienceHackDay/project/faceapp/static/faceapp/models/' + filename + '.obj')


def normalize_vertices(vertices, size):
	normalizer = reduce(lambda base, vert: base + get_length(vert.x, vert.y, vert.z), vertices, 0) / len(vertices)
	for vert in vertices:
		vert.x *= size / normalizer
		vert.y *= size / normalizer
		vert.z *= size / normalizer


def run(mutations, out_filename):
	(vertices, faces, normals) = read_mesh('../Data/model.txt')
	for mutation in mutations:
		mask = read_mask('../Data/Displace/' + mutation + '.txt')
		displace_mask_vertices(mask, vertices, 0.03)

	normalize_vertices(vertices, 1.0)
	print_mesh(vertices, faces, normals, out_filename)


if __name__ == '__main__':
	# run_area('Area')
	run(['ROR2a', 'SATB2b', 'CTNND2a', 'SATB2e', 'DNMT3Bc', 'SEMA3E', 'POLR1Da', 'RAI1d', 'GDF5'], 'run.obj')