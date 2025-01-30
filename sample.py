from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
import asyncio
import os  # osモジュールをインポート
from datetime import datetime  # datetimeモジュールをインポート
from dotenv import load_dotenv


async def main():
	# 環境変数の読み込み
	load_dotenv()
	# Gemini APIの設定
	_api_key = os.getenv("GOOGLE_API_KEY")
	if not _api_key:
		raise ValueError("GOOGLE_API_KEYが設定されていません。.envファイルを確認してください。")


	# Initialize the model
	llm = ChatGoogleGenerativeAI(
		model='gemini-2.0-flash-exp',
		api_key=_api_key
	)

	# Create agent with the model
	agent = Agent(
		task="Find out which anime were popular in Japan in 2005, create a list, and output it in Japanese.",
		llm=llm
	)

	# 実行
	retries = 3
	for attempt in range(retries):
		try:
			result = await agent.run()
			break  # 成功した場合はループを抜ける
		except Exception as e:
			print(f"Error occurred: {e}")
			if "429" in str(e):
				print("429エラーが発生しました。(API上限)30秒待機してから再試行します。")
				await asyncio.sleep(30)  # 5秒待機してから再試行
			else:
				break  # 他のエラーの場合はループを抜ける
	
	# 結果をresultフォルダに保存
	if not os.path.exists('result'):
		os.makedirs('result')  # resultフォルダが存在しない場合は作成
	
	# 現在の日時を取得し、フォーマット
	current_time = datetime.now().strftime("%Y-%m-%d(%H-%M-%S)")
	file_name = f'result/{current_time}.md'  # ファイル名を作成
	
	# 最終結果を取得
	result_str = str(result).replace('\\n', '\n')  # \nを実際の改行に変換
	with open(file_name, 'w', encoding='utf-8') as f:
		f.write(result_str)  # 結果をファイルに書き込む

	# Access (some) useful information
	with open(file_name, 'a', encoding='utf-8') as f:
		f.write("\n\n\n------------------")
		f.write("\nList of visited URLs: " + str(result.urls()))              # List of visited URLs
		f.write("\nNames of executed actions: " + str(result.action_names()))      # Names of executed actions
		f.write("\nAny errors that occurred: " + str(result.errors()))           # Any errors that occurred
		f.write("\nAll actions with their parameters: " + str(result.model_actions()))     # All actions with their parameters

# メインの非同期関数を実行
if __name__ == "__main__":
	asyncio.run(main())