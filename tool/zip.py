import os
import zipfile

def zip_file(filedir):
    """
    压缩文件夹至同名zip文件
    """
    file_news = filedir + '.zip'
    z = zipfile.ZipFile(file_news,'w',zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(filedir):
        fpath = dirpath.replace(filedir,'') #这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()


def unzip(file_name):
    """
    解压缩zip文件至同名文件夹
    """
    zip_ref = zipfile.ZipFile(file_name) # 创建zip 对象
    os.mkdir(file_name.replace(".zip","")) # 创建同名子文件夹
    zip_ref.extractall(file_name.replace(".zip","")) # 解压zip文件内容到子文件夹
    zip_ref.close() # 关闭zip文件


# if __name__ == "__main__":
#     filename = "D:/research/grasp_detection/Grasp_Correction/code-1/img/img_urdf_1"  #要压缩的文件夹路径
#     # zip_file(filename)          # 压缩
#     unzip(filename + '.zip')    # 解压
