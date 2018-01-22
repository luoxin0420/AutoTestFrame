#!/usr/bin/expect
set timeout 5

#expect是在tcl的基础上发展起来的，所以在安装expect之前要先安装tcl。
#为脚本设置参数的值，是通过一个Tcl函数lindex来实现的，该函数从列表/数组得到一个特定的元素。[]用来实现将函数lindex的返回值作为set命令的参数
#spawn – 启动命令
#send – 发送字符串到进程
#expect – 等待来自进程的特定的字符串

set desfolder [lindex $argv 4]
set srcfile [lindex $argv 3]
set pw [lindex $argv 2]
set user [lindex $argv 1]
set host [lindex $argv 0]

spawn scp $user@$host:$srcfile $desfolder

expect {
    "Connection refused" exit
    "Name or service not known" exit
    "continue connecting" {send "yes\r";exp_continue}
    "password:" {send "$pw\r"}

}

expect eof
exit


