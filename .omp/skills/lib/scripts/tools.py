import os

#region 常用目录
omp_file_name = ".omp"
claude_file_name = ".claude"
opencode_file_name = ".opencode"
docs_file_name = "docs"

def GetRootDir() -> str | None:
    localDir = os.getcwd()
    rootDir = None
    if localDir.find(".omp"):
        rootDir = localDir.split(".omp")[0]
        return rootDir
    if localDir.find("docs"):
        rootDir = localDir.split("docs")[0]
        return rootDir
    if localDir.find(".claude"):
        rootDir = localDir.split(".claude")[0]
        return rootDir
    if localDir.find(".claude"):
        rootDir = localDir.split(".claude")[0]
        return rootDir
    return None

rootDir = GetRootDir()
if rootDir is None:
    print("当前目录不是.omp项目目录")
    exit(1)


omp_dir_name = os.path.join(rootDir, omp_file_name) 
docs_dir_name = os.path.join(rootDir, docs_file_name)
#endregion
#======================================================================================================
    
    
if __name__ == "__main__":
    print(GetRootDir())