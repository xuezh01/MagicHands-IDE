'''
遇到问题没人解答？小编创建了一个Python学习交流QQ群：531509025
寻找有志同道合的小伙伴，互帮互助,群里还有不错的视频学习教程和PDF电子书！
'''
import pyperclip
import time


# 稳定不出错

def lihai():
      t = jianting().main()
      print(t)
      return t



class jianting():
    def clipboard_get(self):
        """获取剪贴板数据"""
        data = pyperclip.paste()  # 主要这里差别
        return data

    def main(self):
        """后台脚本：每隔0.2秒，读取剪切板文本，检查有无指定字符或字符串，如果有则执行替换"""
        # recent_txt 存放最近一次剪切板文本，初始化值只多执行一次paste函数读取和替换
        recent_txt = self.clipboard_get()
        while True:
            # txt 存放当前剪切板文本
            txt = self.clipboard_get()
            # 剪切板内容和上一次对比如有变动，再进行内容判断，判断后如果发现有指定字符在其中的话，再执行替换
            if txt != recent_txt:
                # print(f'txt:{txt}')
                recent_txt = txt  # 没查到要替换的子串，返回None
                return recent_txt

                # 检测间隔（延迟0.2秒）
            time.sleep(0.2)


# if __name__ == '__main__':
#     lihai()
