import ast
import random
import string
import os

class Obfuscator(ast.NodeTransformer):
    def __init__(self):
        self.variable_map = {}
        self.function_map = {}
        self.class_map = {}
        self.scope_stack = [{}]
    
    def generate_random_name(self, length=8):
        # 确保生成的名称以字母开头，是合法的Python标识符
        first_char = random.choice(string.ascii_letters)
        rest_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))
        return first_char + rest_chars
    
    def get_scope(self):
        return self.scope_stack[-1]
    
    def visit_FunctionDef(self, node):
        old_name = node.name
        if old_name not in self.function_map:
            new_name = self.generate_random_name()
            self.function_map[old_name] = new_name
        node.name = self.function_map[old_name]
        
        # 处理函数参数
        for arg in node.args.args:
            old_arg_name = arg.arg
            new_arg_name = self.generate_random_name()
            self.get_scope()[old_arg_name] = new_arg_name
            arg.arg = new_arg_name
        
        # 处理默认参数
        if node.args.defaults:
            for default in node.args.defaults:
                self.visit(default)
        
        # 进入新作用域
        self.scope_stack.append({})
        
        # 处理函数体
        for stmt in node.body:
            self.visit(stmt)
        
        # 退出作用域
        self.scope_stack.pop()
        
        return node
    
    def visit_ClassDef(self, node):
        old_name = node.name
        if old_name not in self.class_map:
            new_name = self.generate_random_name()
            self.class_map[old_name] = new_name
        node.name = self.class_map[old_name]
        
        # 进入新作用域
        self.scope_stack.append({})
        
        # 处理类体
        for stmt in node.body:
            self.visit(stmt)
        
        # 退出作用域
        self.scope_stack.pop()
        
        return node
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            # 变量赋值
            if node.id not in self.get_scope():
                new_name = self.generate_random_name()
                self.get_scope()[node.id] = new_name
            node.id = self.get_scope()[node.id]
        elif isinstance(node.ctx, ast.Load):
            # 变量使用
            for scope in reversed(self.scope_stack):
                if node.id in scope:
                    node.id = scope[node.id]
                    break
            # 检查全局映射
            if node.id in self.function_map:
                node.id = self.function_map[node.id]
            elif node.id in self.class_map:
                node.id = self.class_map[node.id]
        return node
    
    def visit_Assign(self, node):
        # 处理赋值语句
        for target in node.targets:
            self.visit(target)
        self.visit(node.value)
        return node
    
    def visit_Call(self, node):
        # 处理函数调用
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            self.visit(kw.value)
        return node
    
    def generate_useless_code(self):
        """生成无用代码"""
        # 生成一些无意义的赋值和计算
        useless_codes = []
        
        # 随机生成几个无用变量和计算
        for _ in range(random.randint(1, 3)):
            var_name = self.generate_random_name()
            # 生成一个复杂但无意义的表达式
            expr = ast.BinOp(
                left=ast.Constant(value=random.randint(1, 100)),
                op=random.choice([ast.Add(), ast.Sub(), ast.Mult(), ast.Div()]),
                right=ast.Constant(value=random.randint(1, 100))
            )
            # 创建赋值语句
            assign = ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=expr
            )
            useless_codes.append(assign)
        
        # 生成一个无意义的条件语句
        if random.random() > 0.5:
            cond = ast.Compare(
                left=ast.Constant(value=random.randint(1, 100)),
                ops=[random.choice([ast.Eq(), ast.NotEq(), ast.Lt(), ast.Gt()])],
                comparators=[ast.Constant(value=random.randint(1, 100))]
            )
            # 无论条件如何，都执行相同的操作（无意义的pass）
            if_stmt = ast.If(
                test=cond,
                body=[ast.Pass()],
                orelse=[ast.Pass()]
            )
            useless_codes.append(if_stmt)
        
        return useless_codes
    
    def visit_FunctionDef(self, node):
        old_name = node.name
        if old_name not in self.function_map:
            new_name = self.generate_random_name()
            self.function_map[old_name] = new_name
        node.name = self.function_map[old_name]
        
        # 处理函数参数
        for arg in node.args.args:
            old_arg_name = arg.arg
            new_arg_name = self.generate_random_name()
            self.get_scope()[old_arg_name] = new_arg_name
            arg.arg = new_arg_name
        
        # 处理默认参数
        if node.args.defaults:
            for default in node.args.defaults:
                self.visit(default)
        
        # 进入新作用域
        self.scope_stack.append({})
        
        # 处理函数体
        new_body = []
        for stmt in node.body:
            # 在语句前插入无用代码
            if random.random() > 0.7:
                new_body.extend(self.generate_useless_code())
            # 处理当前语句
            new_body.append(self.visit(stmt))
            # 在语句后插入无用代码
            if random.random() > 0.7:
                new_body.extend(self.generate_useless_code())
        node.body = new_body
        
        # 退出作用域
        self.scope_stack.pop()
        
        return node
    
    def visit_If(self, node):
        # 处理if语句
        self.visit(node.test)
        
        # 在条件前插入无用代码
        if random.random() > 0.5:
            node.body = self.generate_useless_code() + [self.visit(stmt) for stmt in node.body]
        else:
            node.body = [self.visit(stmt) for stmt in node.body]
        
        # 处理else分支
        if node.orelse:
            if random.random() > 0.5:
                node.orelse = self.generate_useless_code() + [self.visit(stmt) for stmt in node.orelse]
            else:
                node.orelse = [self.visit(stmt) for stmt in node.orelse]
        
        return node
    
    def visit_While(self, node):
        # 处理while语句
        self.visit(node.test)
        
        # 在循环体前插入无用代码
        if random.random() > 0.5:
            node.body = self.generate_useless_code() + [self.visit(stmt) for stmt in node.body]
        else:
            node.body = [self.visit(stmt) for stmt in node.body]
        
        # 处理else分支
        if node.orelse:
            if random.random() > 0.5:
                node.orelse = self.generate_useless_code() + [self.visit(stmt) for stmt in node.orelse]
            else:
                node.orelse = [self.visit(stmt) for stmt in node.orelse]
        
        return node
    
    def visit_For(self, node):
        # 处理for语句
        self.visit(node.target)
        self.visit(node.iter)
        
        # 在循环体前插入无用代码
        if random.random() > 0.5:
            node.body = self.generate_useless_code() + [self.visit(stmt) for stmt in node.body]
        else:
            node.body = [self.visit(stmt) for stmt in node.body]
        
        # 处理else分支
        if node.orelse:
            if random.random() > 0.5:
                node.orelse = self.generate_useless_code() + [self.visit(stmt) for stmt in node.orelse]
            else:
                node.orelse = [self.visit(stmt) for stmt in node.orelse]
        
        return node

def obfuscate_code(code):
    """混淆Python代码"""
    # 解析代码
    tree = ast.parse(code)
    
    # 创建混淆器实例
    obfuscator = Obfuscator()
    
    # 遍历AST并进行混淆
    obfuscated_tree = obfuscator.visit(tree)
    
    # 修复AST
    ast.fix_missing_locations(obfuscated_tree)
    
    # 生成混淆后的代码
    obfuscated_code = ast.unparse(obfuscated_tree)
    
    return obfuscated_code

def obfuscate_file(input_file, output_file):
    """混淆Python文件并保存到输出文件"""
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 混淆代码
    obfuscated_code = obfuscate_code(code)
    
    # 保存到输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(obfuscated_code)
    
    print(f"代码已混淆并保存到: {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Python代码混淆工具")
    parser.add_argument("input", help="输入Python文件路径")
    parser.add_argument("output", help="输出混淆后文件路径")
    
    args = parser.parse_args()
    
    obfuscate_file(args.input, args.output)
