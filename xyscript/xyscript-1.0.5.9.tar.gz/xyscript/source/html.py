diagnosemail_header = \
    """
    <head>
        <title></title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .content{
                padding: 20px;
                border:10px solid rgb(108, 172, 218)
            }
            .file-content{
                display: inline-block;
            }
            .file-content span{
                display: block;
                text-align:center;
            }
            .file-content a{
                text-decoration: none;
                color:black;
            }
            .result_table{
                width:100%;
                border:0;
                cellspacing:1; 
                cellpadding:0;
                border-collapse: collapse;
            }
            .table-header td{
                color: white;
            }
            table td{
                padding-left: 10px;
            }
            table,table tr th, table tr td {
                border:1px solid #ccc;
                }
            table tr td a{
                text-decoration: none;
                color:#1b69b6;
            }
            #result-text{
                width: 70%;
                resize: none;
            }
        </style>
    </head>
    """

diagnosemail_body = \
    """
    <body>
        <div class="content">
            <h4>您好：</h4>
            <h4>&nbsp;&nbsp;&nbsp;&nbsp;针对您最近一次的提交，诊断结果如下：</h4>
            <table class="result_table" >
                <tr class="table-header" style="background-color: gray">
                    <td>名称</td>
                    <td>内容</td>
                    <td>备注</td>
                </tr>
                <tr>
                    <td>project name</td>
                    <td><a href="{project_url}">{project_name}</a></td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td>commit user</td>
                    <td>{user_name}</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td>branch</td>
                    <td>{branch_name}</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td>commit</td>
                    <td>{commit_content}</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td>commit id</td>
                    <td><a href="{commit_url}">{commit_id}</a></td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td>commit date</td>
                    <td>{date}</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td>diagnose result</td>
                    <td>{result}</td>
                    <td>&nbsp;</td>
                </tr>
            </table>
            <h4 >diagnose detail:</h4>
            <textarea name="" id="result-text" rows="10" readonly>{result_detail}</textarea>
            <h4>更多详情见附件</h4>
            <img src="cid:image1" alt="" style="display:none;">
        </div>
    </body>
    """

mergemail_body = \
        """
        <body>
        <div class="content">
            <h4>您好：</h4>
            <h4>&nbsp;&nbsp;&nbsp;&nbsp;针对iOS项目最近一次的代码合并，结果如下：</h4>
            <h5>项目名称：{project_name}</h5>
            <h5>合并分支：{package_branch}</h5>
            <h5>本次合并时间：{start_time}</h5>
            <h5>上一次合并时间：{end_time}</h5>

            <H3>壳工程</H3>
            <table class="result_table_shell" >
                <tr class="table-header" style="background-color: gray">
                    <td>提交人</td>
                    <td>提交时间</td>
                    <td>提交内容</td>
                    <td>备注</td>
                </tr>
                <&shell_list&>
            </table>
            <&submodule_list&>
            <&private_modules&>
        </div>
    </body>
        """

if __name__ == "__main__":
    print(diagnosemail_body)
