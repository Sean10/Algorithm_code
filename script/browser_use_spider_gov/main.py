from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def save_content(title, content):
    # 创建保存目录
    save_dir = "crawled_content"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 生成文件名（使用标题和时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_dir}/{timestamp}_{title[:30]}.txt"
    
    # 保存内容
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"标题: {title}\n\n")
        f.write(f"内容:\n{content}")

async def main():
    agent = Agent(
        task="""
        你是一个网页爬虫助手，请按照以下步骤执行任务：

        1. 使用 goto_page 函数访问 https://hd.ghzyj.sh.gov.cn/2017/zdxxgk/zdbc/index_2.html
        2. 使用 get_elements 函数获取页面上的所有文章标题和链接
        3. 对于每个标题，如果包含"浦东新区"：
           - 使用 click 函数点击文章链接
           - 使用 get_text 函数获取文章内容
           - 检查内容是否包含"合庆镇"或"跃进村"
           - 如果包含，使用 return_json 函数返回文章信息
           - 如果不包含, close 当前tab页, 关闭当前文章页面
        4. 使用 click 函数点击"下一页"，重复步骤2-3，直到文章发布时间为2023年

        每个函数调用后，请等待并检查结果。如果出现错误，使用 retry 函数重试。
        """,
        llm=ChatOpenAI(
            model="deepseek-chat",
            temperature=0
        ),
        use_vision=False
    )
    
    try:
        results = await agent.run()
        print("获取结果:", results)
        
        # 处理返回的结果
        if isinstance(results, str):
            try:
                import json
                # 尝试解析单个文章格式
                article = json.loads(results)
                if isinstance(article, dict) and "title" in article and "content" in article:
                    save_content(article["title"], article["content"])
                    print(f"已保存文章: {article['title']}")
                    if "keywords_found" in article:
                        print(f"找到的关键词: {', '.join(article['keywords_found'])}")
                    if "publish_date" in article:
                        print(f"发布日期: {article['publish_date']}")
            except json.JSONDecodeError:
                print(f"JSON 解析错误，原始结果:", results)
            except Exception as e:
                print(f"处理结果时出错: {e}")
                print("原始结果:", results)
    except Exception as e:
        print(f"执行过程中出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())