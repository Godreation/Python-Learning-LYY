import sys
import os

# 添加当前目录到路径，以便导入红黑树模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from red_black_tree import RedBlackTree

def test_insert_and_search():
    """测试插入和查找操作"""
    print("测试插入和查找操作...")
    rbt = RedBlackTree()
    
    # 插入测试数据
    test_data = [(5, 'five'), (3, 'three'), (7, 'seven'), (2, 'two'), (4, 'four'),
                 (6, 'six'), (8, 'eight'), (1, 'one'), (9, 'nine')]
    
    for key, value in test_data:
        rbt.insert(key, value)
        print(f"插入: {key} -> {value}")
    
    # 测试查找
    print("\n测试查找操作:")
    for key, expected_value in test_data:
        result = rbt.search(key)
        assert result == expected_value, f"查找 {key} 失败，期望 {expected_value}，得到 {result}"
        print(f"查找 {key}: {result} (成功)")
    
    # 测试查找不存在的键
    print("\n测试查找不存在的键:")
    result = rbt.search(10)
    assert result is None, f"查找不存在的键 10 应该返回 None，得到 {result}"
    print(f"查找不存在的键 10: {result} (成功)")
    
    print("插入和查找测试通过！\n")

def test_inorder_traversal():
    """测试中序遍历"""
    print("测试中序遍历...")
    rbt = RedBlackTree()
    
    # 插入测试数据
    test_data = [5, 3, 7, 2, 4, 6, 8]
    for key in test_data:
        rbt.insert(key, str(key))
    
    # 中序遍历应该返回有序结果
    traversal_result = rbt.inorder_traversal()
    traversal_keys = [item[0] for item in traversal_result]
    expected_keys = sorted(test_data)
    
    assert traversal_keys == expected_keys, f"中序遍历结果错误，期望 {expected_keys}，得到 {traversal_keys}"
    print(f"中序遍历结果: {traversal_keys}")
    print("中序遍历测试通过！\n")

def test_delete():
    """测试删除操作"""
    print("测试删除操作...")
    rbt = RedBlackTree()
    
    # 插入测试数据
    test_data = [5, 3, 7, 2, 4, 6, 8, 1, 9]
    for key in test_data:
        rbt.insert(key, str(key))
    
    print(f"初始树中序遍历: {[item[0] for item in rbt.inorder_traversal()]}")
    
    # 测试删除叶子节点
    print("\n测试删除叶子节点 (1):")
    assert rbt.delete(1), "删除 1 失败"
    assert rbt.search(1) is None, "删除后 1 仍然存在"
    print(f"删除后中序遍历: {[item[0] for item in rbt.inorder_traversal()]}")
    
    # 测试删除有一个子节点的节点
    print("\n测试删除有一个子节点的节点 (2):")
    assert rbt.delete(2), "删除 2 失败"
    assert rbt.search(2) is None, "删除后 2 仍然存在"
    print(f"删除后中序遍历: {[item[0] for item in rbt.inorder_traversal()]}")
    
    # 测试删除有两个子节点的节点
    print("\n测试删除有两个子节点的节点 (5):")
    assert rbt.delete(5), "删除 5 失败"
    assert rbt.search(5) is None, "删除后 5 仍然存在"
    print(f"删除后中序遍历: {[item[0] for item in rbt.inorder_traversal()]}")
    
    # 测试删除不存在的键
    print("\n测试删除不存在的键 (10):")
    assert not rbt.delete(10), "删除不存在的键 10 应该返回 False"
    print("删除不存在的键测试通过")
    
    print("删除测试通过！\n")

def test_edge_cases():
    """测试边界情况"""
    print("测试边界情况...")
    
    # 测试空树
    print("\n测试空树:")
    rbt = RedBlackTree()
    assert rbt.search(1) is None, "空树查找应该返回 None"
    assert not rbt.delete(1), "空树删除应该返回 False"
    print("空树测试通过")
    
    # 测试单节点树
    print("\n测试单节点树:")
    rbt = RedBlackTree()
    rbt.insert(1, 'one')
    assert rbt.search(1) == 'one', "单节点树查找失败"
    assert rbt.delete(1), "单节点树删除失败"
    assert rbt.search(1) is None, "单节点树删除后查找应该返回 None"
    print("单节点树测试通过")
    
    print("边界情况测试通过！\n")

def test_large_scale():
    """测试大规模数据"""
    print("测试大规模数据...")
    rbt = RedBlackTree()
    
    # 插入1000个随机键
    import random
    keys = list(range(1000))
    random.shuffle(keys)
    
    print(f"插入 {len(keys)} 个随机键...")
    for i, key in enumerate(keys):
        rbt.insert(key, f'value_{key}')
        if (i + 1) % 200 == 0:
            print(f"已插入 {i + 1} 个键")
    
    # 测试查找
    print("\n测试查找操作...")
    for key in keys:
        result = rbt.search(key)
        assert result == f'value_{key}', f"查找 {key} 失败"
    
    # 测试中序遍历
    print("\n测试中序遍历...")
    traversal_result = rbt.inorder_traversal()
    traversal_keys = [item[0] for item in traversal_result]
    assert traversal_keys == sorted(keys), "中序遍历结果不是有序的"
    
    print("大规模数据测试通过！\n")

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("红黑树测试套件")
    print("=" * 60)
    
    test_insert_and_search()
    test_inorder_traversal()
    test_delete()
    test_edge_cases()
    test_large_scale()
    
    print("=" * 60)
    print("所有测试通过！红黑树实现正确。")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
