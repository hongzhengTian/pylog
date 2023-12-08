import re

def replace_gemm_in_source(source_func):
    # define the pattern to match gemm calls, including the indent
    gemm_pattern = r'([ \t]*)gemm\((\w+),\s*(\w+),\s*(\w+),\s*(\w+),\s*(\w+),\s*["\'](\w+)["\']\)'

    # 定义替换gemm调用的函数
    def replace_gemm_match(match):
        indent, C, A, B, alpha, beta, mode = match.groups()
        
        if mode == 'original':
            loop_code = f"""
{indent}for i in range(len({A})):
{indent}    for j in range(len({B}[0])):
{indent}        dot_results = 0
{indent}        for k in range(len({A}[0])):
{indent}            dot_results += {A}[i, k] * {B}[k, j]
{indent}        {C}[i, j] = {alpha} * dot_results + {beta} * {C}[i, j]
"""
            
        elif mode == 'tiled':
            loop_code = f"""
{indent}for i in range(0, len({A}), 8):
{indent}    for j in range(0, len({B}[0]), 8):
{indent}        if i + 8 > len({A}):
{indent}            ii_bound = len({A})
{indent}        else:
{indent}            ii_bound = i + 8
{indent}        if j + 8 > len({B}[0]):
{indent}            jj_bound = len({B}[0])
{indent}        else:
{indent}            jj_bound = j + 8
{indent}        for ii in range(i, ii_bound):
{indent}            for jj in range(j, jj_bound):
{indent}                dot_results = 0
{indent}                for k in range(len({A}[0])):
{indent}                    dot_results += {A}[ii, k] * {B}[k, jj]
{indent}                {C}[ii, jj] = {alpha} * dot_results + {beta} * {C}[ii, jj]
"""
            
        elif mode == 'unrolled':
            loop_code = f"""
{indent}for i in range(len({A})):
{indent}    for j in range(len({B}[0])):
{indent}        dot_results = 0
{indent}        for k in range(0, len({A}[0]), 4):
{indent}            dot_results += {A}[i, k] * {B}[k, j] + \\
{indent}                           {A}[i, k+1] * {B}[k+1, j] + \\
{indent}                           {A}[i, k+2] * {B}[k+2, j] + \\
{indent}                           {A}[i, k+3] * {B}[k+3, j]
{indent}        {C}[i, j] = {alpha} * dot_results + {beta} * {C}[i, j]
"""
            
        elif mode == 'interchanged':
            loop_code = f"""
{indent}for j in range(len({B}[0])):
{indent}    for i in range(len({A})):
{indent}        dot_results = 0
{indent}        for k in range(len({A}[0])):
{indent}            dot_results += {A}[i, k] * {B}[k, j]
{indent}        {C}[i, j] = {alpha} * dot_results + {beta} * {C}[i, j]
"""
            
        return loop_code

    # 使用正则表达式替换所有gemm调用
    lines = source_func.split('\n')
    for i, line in enumerate(lines):
        if '#' in line and line.find('#') < line.find('gemm'):
            continue
        lines[i] = re.sub(gemm_pattern, replace_gemm_match, line)
    source_func_new = '\n'.join(lines)

    # source_func_new = re.sub(gemm_pattern, replace_gemm_match, source_func)

    return source_func_new