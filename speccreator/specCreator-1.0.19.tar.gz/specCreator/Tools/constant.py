#!/usr/bin/env python
# -*- coding=utf-8 -*-


"""
初始化模板的的时候全局变量
"""
emailSuffix = "@ke.com"
platform = "iOS"
language = "ObjC"
demo = "Yes"
testing = "None"
based = "No"
prefix = "LJ"


"""
标准模板示例Example中需要忽略的内容
"""
ignoreFileString = """

Pods/
Example/Pods/
.config/cafswitcher_config.yml

"""

# "提交脚本，即review.sh  想要提交的时候，主要在命令行运行： sh review.sh 就能提交gerrit"
reviewInfo = """

#bin/bash

git_prefix=".git"

install_commit_msg(){ 
    if [ ! -f ".git/hooks/commit-msg" ]; then
        echo "请输入用户名(不需要加后缀)"
        read username
        gitdir=$(git rev-parse --git-dir); 
        scp -p -P 29418 ${username}@gerrit.lianjia.com:hooks/commit-msg ${gitdir}/hooks/
        if [ ! $? -eq 0 ]; then
            echo "commit-msg下载错误"
            exit 1
        else
            echo "已经存在"
        fi
    fi
}

if [ ! -d "$git_prefix" ]; then
	echo "! [Illegal git repository directory]"
	echo "  移动脚本到git仓库根目录"
	exit 1
fi


if [ ! -d ".git/hooks" ]; then
    mkdir ".git/hooks"
	echo "mkdir successfull"
fi

while getopts "m:c" arg
do
	case $arg in
		m)
		  echo "git commit -a -m ..."
          install_commit_msg
          git commit -a -m "$OPTARG"
          ;;
		c)
		  echo "git commit -a --amend -C HEAD"
          install_commit_msg
          git commit -a --amend -C HEAD;
          ;;
	esac
done


if [ -f ".git/HEAD" ]; then
    head=$(< ".git/HEAD")
    if [[ $head = ref:\ refs/heads/* ]]; then
        git_branch="${head#*/*/}"
    else
        echo "无法获取当前分支"
	    exit 1
    fi

else
    echo "没有git中的HEAD文件"
	exit 1
fi


reviewers=("handa, zhangyansong, yuanyueguang001, zhaohongwei002, songhongri001, lixiangyu004, zhaoxiaomeng001")

echo "当前分支为:$git_branch"

pushUrl="HEAD:refs/for/$git_branch%"
for reviewer in ${reviewers[@]}; do 

    echo "reviewer人员为${reviewer}"    
    pushUrl="${pushUrl}r=${reviewer},"
done
pushUrl="${pushUrl%,*}"
echo "pushUrl为:$pushUrl"
git push origin $pushUrl
if [ $? -eq 0 ]; then
	exit 0
else
	exit 1
fi


"""

noSubSpec = """
    s.preserve_paths = "#{s.name}/Classes/**/*", "#{s.name}/Assets/**/*", "#{s.name}/Framework/**/*", "#{s.name}/Archive/**/*", "#{s.name}/Dependencies/**/*"

    configuration = "Debug"
    if ENV["IS_DEBUG"] || ENV["#{s.name}_DEBUG"]
      configuration = "Debug"
    elsif ENV["IS_RELEASE"] || ENV["#{s.name}_RELEASE"]
      configuration = "Release"
    end

    if ENV['IS_SOURCE'] || ENV["#{s.name}_SOURCE"]
      # 源码部分，请在这里写上必要的。
      s.source_files = "#{s.name}/Classes/**/*.{h,m,mm,c,cpp,cc}"
      s.public_header_files = "#{s.name}/Classes/**/*.h"
      # 如果有自己依赖的库，请写在这里，并且把依赖的.a 或者 .framework 放到Classes 同级别的Dependencies目录下
      # s.source_files = "#{s.name}/Classes/**/*.{h,m,mm,c,cpp,cc}", "#{s.name}/Dependencies/**/*.{h,m,mm,c,cpp,cc}"
      # s.public_header_files = "#{s.name}/Classes/**/*.h", "#{s.name}/Dependencies/**/*.h"
      # ...
    elsif ENV['IS_ARCHIVE'] || ENV["#{s.name}_ARCHIVE"]
      s.public_header_files = "#{s.name}/Archive/#{configuration}/*.h"
      s.source_files = "#{s.name}/Archive/#{configuration}/*.h"
      s.vendored_libraries = "#{s.name}/Archive/#{configuration}/lib#{s.name}.a"
      # 如果源码有依赖的库，上面这一行需要换成下面的
      # s.public_header_files = "#{s.name}/Archive/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.source_files = "#{s.name}/Archive/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.vendored_libraries = "#{s.name}/Archive/#{configuration}/lib#{s.name}.a","#{s.name}/Dependencies/**/*.a"
      # s.vendored_frameworks= "#{s.name}/Dependencies/**/*.framework"
    else
      s.public_header_files = "#{s.name}/Framework/#{configuration}/*.h"
      s.source_files = "#{s.name}/Framework/#{configuration}/*.h"
      s.vendored_frameworks = "#{s.name}/Framework/#{configuration}/#{s.name}.framework"
      # 如果源码有依赖的库，上面的一行酌情换成下面的语句
      # s.public_header_files = "#{s.name}/Framework/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.source_files = "#{s.name}/Framework/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.vendored_frameworks = "#{s.name}/Framework/#{configuration}/#{s.name}.framework","#{s.name}/Dependencies/**/*.framework"
      # s.vendored_libraries = "#{s.name}/Dependencies/**/*.a"
    end
    # 公共部分，比如公共资源类。framework等
    # s.resources        = "#{s.name}/Assets/**/*.{bundle,lic,png,jpg,plist,xib}"
    # 或者
    # s.resource_bundle = {
    #   "#{s.name}" => "#{s.name}/Assets/*.{storyboard,xib,json,xcassets,png,html}"
    # }

 """

packageBySubspec = """

  s.preserve_paths = "#{s.name}/Classes/**/*", "#{s.name}/Assets/**/*", "#{s.name}/Framework/**/*", "#{s.name}/Archive/**/*", "#{s.name}/Dependencies/**/*"

  # :spec_name => 名字
  _Core = {:spec_name => "Core"}
  # :sub_dependency => 内部依赖的数组, 变量是subspec形式的。
  # :resources => 指向资源的路径字符串
  _Foundation = {:spec_name => "Foundation", :resources => "#{s.name}/Assets/**/*.{bundle,lic,png,jpg,plist}" , :sub_dependency => [_Core]}
  # :dependency => 字典元素的数组， 里面每个字典包含两个元素 :name=> 第三方库名字， :version => 版本号(如果不指定，不写)
  _UIKit = {:spec_name => "UIKit", :dependency => [{:name => "AFNetworking", :version => "3.2.0"}]}

  #subspec 的集合
  _subspecs = [_Core, _Foundation, _UIKit]

  configuration = "Debug"
  if ENV["IS_DEBUG"] || ENV["#{s.name}_DEBUG"]
    configuration = "Debug"
  elsif ENV["IS_RELEASE"] || ENV["#{s.name}_RELEASE"]
    configuration = "Release"
  end

  _subspecs.each do |spec|
    if spec.delete(:noSource)
      next
    end
    if ENV["#{s.name}_#{spec[:spec_name]}_SOURCE"] || ENV['IS_SOURCE']
      #源码部分
      spec[:source_files] = "#{s.name}/Classes/#{spec[:spec_name]}/**/*.{h,m,mm,c,cpp,cc}"
      spec[:public_header_files] = "#{s.name}/Classes/#{spec[:spec_name]}/**/*.h"
    elsif ENV["#{s.name}_#{spec[:spec_name]}_ARCHIVE"] || ENV['IS_ARCHIVE']
      spec[:source_files] = "#{s.name}/Archive/#{spec[:spec_name]}/#{configuration}/*.h"
      spec[:public_header_files] = "#{s.name}/Archive/#{spec[:spec_name]}/#{configuration}/*.h"
      spec[:vendored_libraries] = "#{s.name}/Archive/#{spec[:spec_name]}/#{configuration}/*.a"
      # 如果源码有依赖的库，上面这一行需要换成下面的
      # s.public_header_files = "#{s.name}/Archive/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.source_files = "#{s.name}/Archive/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.vendored_libraries = "#{s.name}/Archive/#{configuration}/lib#{s.name}.a","#{s.name}/Dependencies/**/*.a"
      # s.vendored_frameworks= "#{s.name}/Dependencies/**/*.framework"
    else
      spec[:source_files] = "#{s.name}/Framework/#{spec[:spec_name]}/#{configuration}/*.h"
      spec[:public_header_files] = "#{s.name}/Framework/#{spec[:spec_name]}/#{configuration}/*.h"
      spec[:vendored_frameworks] = "#{s.name}/Framework/#{spec[:spec_name]}/#{configuration}/*.framework"
      # 有外部依赖的静态库的话请注释上面一行，换下面的
      # s.public_header_files = "#{s.name}/Framework/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.source_files = "#{s.name}/Framework/#{configuration}/*.h", "#{s.name}/Dependencies/**/*.h"
      # s.vendored_frameworks = "#{s.name}/Framework/#{configuration}/#{s.name}.framework","#{s.name}/Dependencies/**/*.framework"
      # s.vendored_libraries = "#{s.name}/Dependencies/**/*.a"
    end
  end

  _subspecs.each do |spec|
    s.subspec spec[:spec_name] do |ss|
      if spec[:source_files]
        ss.source_files = spec[:source_files]
      end

      if spec[:public_header_files]
        ss.public_header_files = spec[:public_header_files]
      end

      if spec[:vendored_libraries]
        ss.vendored_libraries = spec[:vendored_libraries]
      end

      if spec[:vendored_frameworks]
        ss.vendored_frameworks = spec[:vendored_frameworks]
      end

      if spec[:resources]
        ss.resources = spec[:resources]
      end

      if spec[:sub_dependency]
        spec[:sub_dependency].each do |dep|
          ss.dependency "#{s.name}/#{dep[:spec_name]}"
        end
      end

      if spec[:dependency]
        spec[:dependency].each do |dep|
          if dep.has_key?(:version)
            ss.dependency dep[:name], dep[:version]
          else
            ss.dependency dep[:name]
          end
        end
      end

      if spec[:frameworks]
        spec[:frameworks].each do |f|
          ss.framework = "#{f}"
        end
      end
    end
  end
  # 公共部分
  # ――― Resources ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #
  #
  #  A list of resources included with the Pod. These are copied into the
  #  target bundle with a build phase script. Anything else will be cleaned.
  #  You can preserve files from being cleaned, please don't preserve
  #  non-essential files like tests, examples and documentation.
  #

  # s.resource  = "icon.png"
  # s.resources = "Resources/*.png"

  # ――― Project Linking ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #
  #
  #  Link your library with frameworks, or libraries. Libraries do not include
  #  the lib prefix of their name.
  #
  # 公共部分，比如公共资源类。framework等
  # s.framework  = "SomeFramework"
  # s.frameworks = "SomeFramework", "AnotherFramework" 
  # s.library   = "iconv"
  # s.libraries = "iconv", "xml2" 
  # ――― Project Settings ――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #
  #
  #  If your library depends on compiler flags you can set them in the xcconfig hash
  #  where they will only apply to your library. If you depend on other Podspecs
  #  you can include multiple dependencies to ensure it works.

"""