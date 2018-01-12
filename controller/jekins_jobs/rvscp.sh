#!/usr/bin/expect
set timeout 5

#set pw $2
set desfolder [lindex $argv 4]
set srcfile [lindex $argv 3]
set pw [lindex $argv 2]
set user [lindex $argv 1]
set host [lindex $argv 0]
#set host $1
spawn scp $srcfile $user@$host:$desfolder

expect {
    "Connection refused" exit
    "Name or service not known" exit
    "continue connecting" {send "yes\r";exp_continue}
    "password:" {send "$pw\r"}
    #"Last login" {send "$cmd\n";exp_continue}
    #"#" exit
}


expect eof
exit

#./ssh_nopass.sh 192.168.0.212 111111 ls
