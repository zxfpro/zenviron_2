#!/usr/bin/env python3
"""
MySQL 数据库快速初始化脚本

该脚本会读取 migrations/init_all_tables.sql 文件并执行所有建表语句。

用法:
    python scripts/init_db_mysql.py
    python scripts/init_db_mysql.py --host localhost --port 3306 --user root --password 123456 --database test_db
"""
import argparse
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.config import settings
    import pymysql
except ImportError as e:
    print(f"错误: 缺少必要的依赖包: {str(e)}")
    print("请运行: pip install pymysql")
    sys.exit(1)


def execute_sql_file(connection, sql_file_path: str):
    """
    执行 SQL 文件
    
    Args:
        connection: MySQL 连接对象
        sql_file_path: SQL 文件路径
    """
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割 SQL 语句（以分号分隔，但需要处理注释和字符串中的分号）
    statements = []
    current_statement = ""
    in_string = False
    string_char = None
    
    for line in sql_content.split('\n'):
        # 跳过注释行
        line_stripped = line.strip()
        if line_stripped.startswith('--') or not line_stripped:
            continue
        
        for char in line:
            if char in ("'", '"', '`') and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            
            current_statement += char
            
            if char == ';' and not in_string:
                stmt = current_statement.strip()
                if stmt:
                    statements.append(stmt)
                current_statement = ""
    
    # 执行所有语句
    cursor = connection.cursor()
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        try:
            cursor.execute(statement)
            success_count += 1
            print(f"✓ 执行语句 {i}/{len(statements)}: {statement[:50]}...")
        except Exception as e:
            error_count += 1
            print(f"✗ 执行语句 {i} 失败: {str(e)}")
            print(f"  语句: {statement[:100]}...")
    
    connection.commit()
    cursor.close()
    
    print(f"\n执行完成: 成功 {success_count} 条，失败 {error_count} 条")
    return error_count == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MySQL 数据库快速初始化")
    parser.add_argument("--host", default=settings.DB_HOST, help="数据库主机")
    parser.add_argument("--port", type=int, default=settings.DB_PORT, help="数据库端口")
    parser.add_argument("--user", default=settings.DB_USER, help="数据库用户")
    parser.add_argument("--password", default=settings.DB_PASSWORD, help="数据库密码")
    parser.add_argument("--database", default=settings.DB_NAME, help="数据库名称")
    parser.add_argument("--sql-file", default="migrations/init_all_tables.sql", help="SQL 文件路径")
    
    args = parser.parse_args()
    
    # 检查 SQL 文件是否存在
    sql_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        args.sql_file
    )
    
    if not os.path.exists(sql_file_path):
        print(f"错误: SQL 文件不存在: {sql_file_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("MySQL 数据库初始化")
    print("=" * 60)
    print(f"主机: {args.host}:{args.port}")
    print(f"数据库: {args.database}")
    print(f"用户: {args.user}")
    print(f"SQL 文件: {sql_file_path}")
    print("=" * 60)
    
    try:
        # 连接数据库
        print("\n正在连接数据库...")
        connection = pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✓ 数据库连接成功")
        
        # 执行 SQL 文件
        print(f"\n正在执行 SQL 文件: {sql_file_path}")
        success = execute_sql_file(connection, sql_file_path)
        
        connection.close()
        
        if success:
            print("\n✓ 数据库初始化成功！")
            sys.exit(0)
        else:
            print("\n✗ 数据库初始化失败，请检查错误信息")
            sys.exit(1)
    
    except pymysql.Error as e:
        print(f"\n✗ 数据库连接失败: {str(e)}")
        print("\n请检查:")
        print("  1. 数据库服务是否已启动")
        print("  2. 数据库名称是否存在（如果不存在，请先创建数据库）")
        print("  3. 用户名和密码是否正确")
        print("  4. 网络连接是否正常")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
