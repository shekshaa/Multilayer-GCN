import numpy as np
import pandas as pd
import scipy.sparse as sp
from gcn.utils import sparse_to_tuple


def get_indices(df):
    indices = []
    for item in df.values:
        s = item[0].split(' ')
        indices.append([int(s[0]), int(s[1])])
    return np.asarray(indices)


def get_features(df):
    features = []
    for item in df.values:
        s = item[0].split(' ')
        row = [int(s[j]) for j in range(1, len(s))]
        features.append(row)
    return np.asarray(features)


def make_sparse_matrix(indices, shape):
    data = np.ones(indices.shape[0])
    return sp.csr_matrix((data, (indices[:, 0], indices[:, 1])), shape=shape)


def make_node_types(n0, n1, n2):
    n_total = n0 + n1 + n2
    node_types = np.zeros((n_total,), dtype=int)
    node_types[: n0] = 0
    node_types[n0: n0 + n1] = 1
    node_types[n0 + n1:] = 2
    one_hot_node_types = np.zeros((n_total, 3), dtype=int)
    one_hot_node_types[np.arange(n_total), node_types] = 1
    return one_hot_node_types


def load_aminer():
    df0 = pd.read_csv('./data/aminer/aminer.adj0')
    df1 = pd.read_csv('./data/aminer/aminer.adj1')
    df2 = pd.read_csv('./data/aminer/aminer.adj2')

    adj0_indices = get_indices(df0)
    adj1_indices = get_indices(df1)
    adj2_indices = get_indices(df2)

    n0 = np.max(adj0_indices, axis=0)[0] + 1
    n1 = np.max(adj1_indices, axis=0)[0] + 1
    n2 = np.max(adj2_indices, axis=0)[0] + 1
    n_total = n0 + n1 + n2

    adj0 = make_sparse_matrix(adj0_indices, (n0, n0))
    adj1 = make_sparse_matrix(adj1_indices, (n1, n1))
    adj2 = make_sparse_matrix(adj2_indices, (n2, n2))

    df01 = pd.read_csv('./data/aminer/aminer.bet0_1')
    df02 = pd.read_csv('./data/aminer/aminer.bet0_2')

    adj01_indices = get_indices(df01)
    adj02_indices = get_indices(df02)

    adj01 = make_sparse_matrix(adj01_indices, (n0, n1))
    adj02 = make_sparse_matrix(adj02_indices, (n0, n2))

    r0 = sp.hstack((adj0, adj01, adj02))
    r1 = sp.hstack((adj01.transpose(), adj1, sp.csr_matrix(np.zeros(shape=(n1, n2), dtype=int))))
    r2 = sp.hstack((adj02.transpose(), sp.csr_matrix(np.zeros(shape=(n2, n1), dtype=int)), adj2))

    total_adj = sp.vstack((r0, r1, r2))

    features = sp.csr_matrix(np.ones((n_total, n_total), dtype=int))

    return features, total_adj, make_node_types(n0, n1, n2)


def load_infra():
    df0 = pd.read_csv('./data/infra/infra.adj0')
    df1 = pd.read_csv('./data/infra/infra.adj1')
    df2 = pd.read_csv('./data/infra/infra.adj2')

    adj0_indices = get_indices(df0)
    adj1_indices = get_indices(df1)
    adj2_indices = get_indices(df2)

    n0 = np.max(adj0_indices, axis=0)[0] + 1
    n1 = np.max(adj1_indices, axis=0)[0] + 1
    n2 = np.max(adj2_indices, axis=0)[0] + 1

    adj0 = make_sparse_matrix(adj0_indices, (n0, n0))
    adj1 = make_sparse_matrix(adj1_indices, (n1, n1))
    adj2 = make_sparse_matrix(adj2_indices, (n2, n2))

    df01 = pd.read_csv('./data/infra/infra.bet0_1')
    df02 = pd.read_csv('./data/infra/infra.bet0_2')
    df12 = pd.read_csv('./data/infra/infra.bet1_2')

    adj01_indices = get_indices(df01)
    adj02_indices = get_indices(df02)
    adj12_indices = get_indices(df12)

    adj01 = make_sparse_matrix(adj01_indices, (n0, n1))
    adj02 = make_sparse_matrix(adj02_indices, (n0, n2))
    adj12 = make_sparse_matrix(adj12_indices, (n1, n2))

    r0 = sp.hstack((adj0, adj01, adj02))
    r1 = sp.hstack((adj01.transpose(), adj1, adj12))
    r2 = sp.hstack((adj02.transpose(), adj12.transpose(), adj2))

    total_adj = sp.vstack((r0, r1, r2))

    features = sp.csr_matrix(np.ones(total_adj.shape, dtype=int))

    return features, total_adj, make_node_types(n0, n1, n2)


def load_feature_adj_types(dataset=None):
    feature = np.random.rand(1000, 500)
    adj = np.random.randint(low=0, high=2, size=(1000, 1000))
    sparse_feature = sp.csr_matrix(feature)
    sparse_adj = sp.csr_matrix(adj)
    node_types = np.random.randint(low=0, high=3, size=(1000,))
    one_hot_types = np.zeros(shape=(1000, 3), dtype=int)
    one_hot_types[np.arange(1000), node_types] = 1
    return sparse_feature, sparse_adj, one_hot_types


def selection(mat, val_prop, test_prop):
    mat_triu = sp.triu(mat)
    mat_tuple = sparse_to_tuple(mat_triu)
    elements = mat_tuple[0]

    all_edge_idx = list(range(elements.shape[0]))
    np.random.shuffle(all_edge_idx)

    num_val = int(np.floor(elements.shape[0] * val_prop))
    val_edge_idx = all_edge_idx[:num_val]
    val_edges = elements[val_edge_idx]

    num_test = int(np.floor(elements.shape[0] * test_prop))
    test_edge_idx = all_edge_idx[num_val:(num_val + num_test)]
    test_edges = elements[test_edge_idx]

    train_edges = np.delete(elements, np.hstack([test_edge_idx, val_edge_idx]), axis=0)
    return train_edges, val_edges, test_edges


def masking(true_indices, false_indices, shape):
    template_mask = np.zeros(shape=shape, dtype=int)
    template_mask[true_indices] = 1
    template_mask[false_indices] = 1
    return template_mask


def load_train_val_test(adj):
    complement = sp.csr_matrix(np.ones(shape=adj.shape, dtype=int)) - adj

    non_edges = complement - sp.dia_matrix((complement.diagonal()[np.newaxis, :], [0]), shape=complement.shape)
    non_edges.eliminate_zeros()

    edges = adj - sp.dia_matrix((adj.diagonal()[np.newaxis, :], [0]), shape=adj.shape)
    edges.eliminate_zeros()

    train_edges, val_edges, test_edges = selection(edges, 0.05, 0.1)
    train_false_edges, val_false_edges, test_false_edges = selection(non_edges, 0.05, 0.1)

    train_mask = masking(train_edges, train_false_edges, shape=adj.shape)
    val_mask = masking(val_edges, val_false_edges, shape=adj.shape)
    test_mask = masking(test_edges, test_false_edges, shape=adj.shape)

    train_mask = train_mask + train_mask.T
    val_mask = val_mask + val_mask.T
    test_mask = test_mask + test_mask.T

    data = np.ones(train_edges.shape[0])
    adj_train = sp.csr_matrix((data, (train_edges[:, 0], train_edges[:, 1])), shape=adj.shape)
    adj_train = adj_train + adj_train.T

    return adj_train, train_mask, val_mask, test_mask

# def load_train_val_test(adj):
#     adj = adj - sp.dia_matrix((adj.diagonal()[np.newaxis, :], [0]), shape=adj.shape)
#     adj.eliminate_zeros()
#     # Check that diag is zero:
#     assert np.diag(adj.todense()).sum() == 0
#
#     adj_triu = sp.triu(adj)
#     adj_tuple = sparse_to_tuple(adj_triu)
#     edges = adj_tuple[0]
#     edges_all = sparse_to_tuple(adj)[0]
#     num_test = int(np.floor(edges.shape[0] / 10.))
#     num_val = int(np.floor(edges.shape[0] / 20.))
#
#     all_edge_idx = list(range(edges.shape[0]))
#     np.random.shuffle(all_edge_idx)
#     val_edge_idx = all_edge_idx[:num_val]
#     test_edge_idx = all_edge_idx[num_val:(num_val + num_test)]
#     test_edges = edges[test_edge_idx]
#     val_edges = edges[val_edge_idx]
#     train_edges = np.delete(edges, np.hstack([test_edge_idx, val_edge_idx]), axis=0)
#
#     def ismember(a, b, tol=5):
#         rows_close = np.all(np.round(a - b[:, None], tol) == 0, axis=-1)
#         return np.any(rows_close)
#
#     test_edges_false = []
#     while len(test_edges_false) < len(test_edges):
#         idx_i = np.random.randint(0, adj.shape[0])
#         idx_j = np.random.randint(0, adj.shape[0])
#         if idx_i == idx_j:
#             continue
#         if ismember([idx_i, idx_j], edges_all):
#             continue
#         if test_edges_false:
#             if ismember([idx_j, idx_i], np.array(test_edges_false)):
#                 continue
#             if ismember([idx_i, idx_j], np.array(test_edges_false)):
#                 continue
#         test_edges_false.append([idx_i, idx_j])
#
#     val_edges_false = []
#     while len(val_edges_false) < len(val_edges):
#         idx_i = np.random.randint(0, adj.shape[0])
#         idx_j = np.random.randint(0, adj.shape[0])
#         if idx_i == idx_j:
#             continue
#         if ismember([idx_i, idx_j], edges_all):
#             continue
#         if ismember([idx_i, idx_j], test_edges):
#             continue
#         if ismember([idx_j, idx_i], test_edges):
#             continue
#         if val_edges_false:
#             if ismember([idx_j, idx_i], np.array(val_edges_false)):
#                 continue
#             if ismember([idx_i, idx_j], np.array(val_edges_false)):
#                 continue
#         val_edges_false.append([idx_i, idx_j])
#
#     assert ~ismember(test_edges_false, edges_all)
#     assert ~ismember(val_edges_false, edges_all)
#     assert ~ismember(val_edges, train_edges)
#     assert ~ismember(test_edges, train_edges)
#     assert ~ismember(val_edges, test_edges)
#
#     data = np.ones(train_edges.shape[0])
#
#     # Re-build adj matrix
#     train_mask = sp.csr_matrix((data, (train_edges[:, 0], train_edges[:, 1])), shape=adj.shape)
#
#     #
#     # # NOTE: these edge lists only contain single direction of edge!
#
#
#     return train_edges, val_edges, val_edges_false, test_edges, test_edges_false
