#导入新的测试集， 第一个参数是需要导入的用例文件，格式参考模板。 第二个参数是生成的XML文件，指定文件名即可
#程序会自动生成，生成的测试集名称是“Test_时间戳"

E:\AutoTestFrame\testlink>import.py -i E:/book2.csv -o E:/test3.xml

# 也可指定测试集名，请确保该测试集名在TESTLINK同一级用例集中不重名

E:\AutoTestFrame\testlink>import.py -i E:/book2.csv -o E:/test3.xml -n 测试

# 往已存在用例集中导入用例, 得到XML文件后，在TESTLINK中选中需要导入用例的的测试集，然后点击导入用例的按钮

E:\AutoTestFrame\testlink>import.py -i E:/book2.csv -o E:/test3.xml -f True




#把导出xml文件转成csv(格式同csv模板相同）
E:\AutoTestFrame\testlink>export.py -i E:/启动注册.testsuite-deep.xml -o E:/output.csv