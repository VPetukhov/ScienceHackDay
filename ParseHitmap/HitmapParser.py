from os import listdir
import os
from PIL import Image
import numpy as np


def revert_color(color, scale):
	return scale[color[0]][color[1]][color[2]]


def parse_heatmap(heatmap_filename, scale):
    #TODO preprocess heatmap
	res = []
	with Image.open(heatmap_filename) as heatmap:
		heatmap = heatmap.convert(mode='RGB')
		colors = np.asarray(heatmap)
		for row in colors:
			row_res = []
			for c in row:
				row_res.append(revert_color(c, scale) if int(c[0]) + c[1] + c[2] < 700 else -1)
			res.append(row_res)

	return res


def get_colormap():
	scale = [[[0] * 256] * 256] * 256
	r = 0; g = 0; b = 0;
	index = 0

	while b <= 255:
		scale[r][g][b] = index
		index += 1
		b += 1

	b = 255
	while g <= 255:
		scale[r][g][b] = index
		index += 1
		g += 1

	g = 255
	while r <= 255:
		scale[r][g][b] = index
		index += 1
		r += 1

	r = 255
	while b >= 0:
		scale[r][g][b] = index
		index += 1
		b -= 1

	b = 0
	while g >= 0:
		scale[r][g][b] = index
		index += 1
		g -= 1

	return scale


def get_colormap_S34():
	scale = [[[0] * 256] * 256] * 256
	r = 0; g = 0; b = 144
	index = 0

	while b <= 255:
		scale[r][g][b] = index
		index += 1
		b += 1

	b = 255
	while g <= 255:
		scale[r][g][b] = index
		index += 1
		g += 1

	g = 255
	while r <= 255:
		scale[r][g][b] = index
		index += 1
		r += 1
		b -= 1

	r = 255
	b = 0
	while g >= 0:
		scale[r][g][b] = index
		index += 1
		g -= 1

	g = 0
	while r >= 100:
		scale[r][g][b] = index
		index += 1
		r -= 1

	return scale


def save_matrix(matrix, filename):
	with open(filename, mode='w') as file:
		for row in matrix:
			for c in row:
				file.write('%.3f ' % (c))
			file.write('\n')


def cut_matrix(matrix):
	start_row = 0; end_row = len(matrix) - 1
	start_col = 0; end_col = len(matrix[0]) - 1

	while len(list(filter(lambda c: c != -1, matrix[start_row]))) == 0:
		start_row += 1

	while len(list(filter(lambda c: c != -1, matrix[end_row]))) == 0:
		end_row -= 1

	flag = True
	while flag:
		for i in range(len(matrix)):
			if matrix[i][start_col] != -1:
				flag = False
				break
		start_col += 1

	flag = True
	while flag:
		for i in range(len(matrix)):
			if matrix[i][end_col] != -1:
				flag = False
				break
		end_col -= 1

	return list(m[start_col - 1:end_col + 2] for m in matrix[start_row:end_row + 1])


def normalize_matrix(matrix, mid_index, min_scale, max_scale):
	max_ind = max(matrix, key=lambda row: max([r for r in row if r != -1]))
	min_ind = min(matrix, key=lambda row: min([r for r in row if r != -1]))

	positive_scale = max_scale / (max_ind - mid_index)
	negative_scale = min_scale / (mid_index - min_ind)

	for row in matrix:
		for i in range(len(row)):
			if row[i] == -1:
				continue

			if row[i] > mid_index:
				row[i] = (row[i] - mid_index) * positive_scale
			else:
				row[i] = (mid_index - row[i]) * negative_scale


def normalize_matrix_S34(matrix, max_ind):
	for row in matrix:
		for i in range(len(row)):
			if row[i] == -1:
				continue

			row[i] /= max_ind


def normalize_matrix_S39(matrix, mid_ind, max_ind):
	for row in matrix:
		for i in range(len(row)):
			if row[i] == -1:
				continue

			row[i] = (row[i] - mid_ind) / max_ind


def run(filename):
	scale = get_colormap_S34()
	# matrix = parse_heatmap('/Work/SHD/Heatmaps/Cutted/' + filename + '.png', scale)
	matrix = parse_heatmap('/Work/SHD/Heatmaps/Cutted/Displace/' + filename + '.png', scale)
	matrix = cut_matrix(matrix)
	normalize_matrix_S34(matrix, scale[100][0][0]) #TODO Parameters
	# normalize_matrix_S39(matrix, scale[127][255][127], scale[100][0][0]) #TODO Parameters
	save_matrix(matrix, filename + '.txt')


if __name__ == '__main__':
	# for f_name in listdir("/Work/SHD/Heatmaps/Cutted/Displace/"):
	# 	name = os.path.splitext(f_name)[0]
	# 	run(name)

	run('Sex')
	# run('WNT30')
	# run('Area')
