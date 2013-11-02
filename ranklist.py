# -*- coding: utf-8 -*-

DEFAULT_SIZE = 1024
DEFAULT_MAX_DEPTH = 23

def bisect_left(a, x, cmper):
	lo = 0
	hi = len(a)
	while lo < hi:
		mid = (lo + hi) // 2
		if cmper(a[mid], x) < 0:
			lo = mid + 1
		else :
			hi = mid
	return lo

'''
    0  1  2  3  4  5  6    n-2 n-1 n
    |--|--|--|--|--|--|.....|--|--|
   low                           high

以区间端点分割
'''
class Ranklist(object):
	#interval_range 表示线段长度
	def __init__(self, interval_range = DEFAULT_SIZE, key_sorter = None, \
			max_depth = DEFAULT_MAX_DEPTH):
		self.max_depth = max_depth
		self.key_sorter = key_sorter
		self.low = [None for _ in xrange(4 * interval_range + 1)]
		self.high = [None for _ in xrange(4 * interval_range + 1)]
		self.cnt = [0 for _ in xrange(4 * interval_range + 1)]
		self.ordered_guid_list = [None for _ in xrange(4 * interval_range + 1)]
		self.interval_range = interval_range
		self._make_tree(0, 0, interval_range, 0)

	def _make_tree(self, idx, low, high, depth):
		self.high[idx] = high
		self.low[idx] = low
		if high - low == 1 or depth == self.max_depth:
			return
		self._make_tree(2*idx + 1, low, (low + high) // 2, depth + 1)
		self._make_tree(2*idx + 2, (low + high) // 2, high, depth + 1)

	def _insert(self, idx, key, guid, depth):
		mid = (self.low[idx] + self.high[idx]) // 2
		if (self.high[idx] - self.low[idx]) == 1 or depth == self.max_depth:
			if self.ordered_guid_list[idx] is not None and \
					guid in self.ordered_guid_list[idx]:
				raise RuntimeError('interval_tree insert duplicate', \
						'guid', guid)

			if self.ordered_guid_list[idx] is None:
				self.ordered_guid_list[idx] = []
			if self.key_sorter is None:
				self.ordered_guid_list[idx].append(guid)
			else :
				insert_point = bisect_left(self.ordered_guid_list[idx], \
						guid, self.key_sorter)
				self.ordered_guid_list[idx].insert(insert_point, guid)
		elif mid >= key:
			self._insert(2*idx + 1, key, guid, depth + 1)
		else :
			self._insert(2*idx + 2, key, guid, depth + 1)
		self.cnt[idx] += 1

	def _delete(self, idx, key, guid, depth):
		assert(self.cnt[idx] > 0)
		mid = (self.low[idx] + self.high[idx]) // 2
		if (self.high[idx] - self.low[idx]) == 1 or depth == self.max_depth:
			if self.ordered_guid_list[idx] is None or \
					guid not in self.ordered_guid_list[idx]:
				raise RuntimeError('interval_tree delete fail', 'guid', guid)
			self.ordered_guid_list[idx].remove(guid)
		elif key <= mid:
			self._delete(2*idx+1, key, guid, depth + 1)
		else :
			self._delete(2*idx+2, key, guid, depth + 1)
		self.cnt[idx] -= 1

	def _query_rank(self, idx, key, guid, depth):
		mid = (self.low[idx] + self.high[idx]) // 2
		if (self.high[idx] - self.low[idx]) == 1 or depth == self.max_depth:
			assert(self.ordered_guid_list[idx] is not None and guid in \
					self.ordered_guid_list[idx])
			return self.ordered_guid_list[idx].index(guid) + 1
		if key <= mid:
			return self.cnt[2*idx+2] + self._query_rank(2*idx+1, key, guid, depth + 1)
		else :
			return self._query_rank(2*idx+2, key, guid, depth + 1)

	# [begin_rank, end_rank]
	def _query_range(self, idx, begin_rank, end_rank, depth):
		if (self.high[idx] - self.low[idx]) == 1 or depth == self.max_depth:
			if self.ordered_guid_list[idx] is None:
				return []
			return self.ordered_guid_list[idx][begin_rank - 1 : end_rank]
		r_cnt = self.cnt[2*idx+2]
		if r_cnt >= end_rank:
			return self._query_range(2*idx+2, begin_rank, end_rank, depth + 1)
		elif r_cnt < begin_rank:
			return self._query_range(2*idx+1, begin_rank - r_cnt, end_rank - r_cnt, depth + 1)
		else :
			lst = self._query_range(2*idx+2, begin_rank, r_cnt, depth + 1)
			lst.extend(self._query_range(2*idx+1, 1, end_rank - r_cnt, depth + 1))
			return lst

	def Insert(self, key, guid):
		if key <= 0 or key > self.interval_range:
			raise RuntimeError('interval tree query range error')
		self._insert(0, key, guid, 0)

	def Delete(self, key, guid):
		if key <= 0 or key > self.interval_range:
			raise RuntimeError('interval tree query range error')
		self._delete(0, key, guid, 0)

	def QueryRank(self, key, guid):
		if key <= 0 or key > self.interval_range:
			raise RuntimeError('interval tree query range error')
		return self._query_rank(0, key, guid, 0)

	#begin_rank indexed from 1, [begin_rank, end_rank]
	def QueryRange(self, begin_rank, end_rank):
		if begin_rank <= 0:
			raise RuntimeError('interval tree query range starts from 1')
		if begin_rank > end_rank:
			raise RuntimeError('interval tree query start rank error')
		return self._query_range(0, begin_rank, end_rank, 0)

	def GetTotalCount(self):
		return self.cnt[0]

#sample
guid2info = {}

def func(id1, id2):
	info1 = guid2info[id1]
	info2 = guid2info[id2]
	ret = info1[0] - info2[0]
	if ret != 0:
		return -ret
	return info1[1] - info2[1]

if __name__ == '__main__':
	global DEFAULT_MAX_DEPTH
	#DEFAULT_MAX_DEPTH = 2
	import random
	import time
	SCORE_MAX = 20
	POPULATION = 100
	for i in xrange(POPULATION):
		guid2info[i] = (random.randint(1, SCORE_MAX), random.randint(1, 5), )

	begin = time.time()
	t = Ranklist(SCORE_MAX + 1, func)
	for k, v in guid2info.iteritems():
		t.Insert(v[0], k)
	print time.time() - begin
	begin = time.time()
	for k, v in guid2info.iteritems():
		print k, v, t.QueryRank(v[0], k)
	print time.time() - begin
	begin = time.time()
	for i in xrange(49000):
		t.QueryRange(i+1, i+9)
	print time.time() - begin
	begin = time.time()
	for k, v in guid2info.iteritems():
		t.Delete(v[0], k)
	print time.time() - begin
