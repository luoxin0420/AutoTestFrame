#!/usr/bin/expect
set timeout -1

#set pw $2
set cmd [lindex $argv 3]
set pw [lindex $argv 2]
set user [lindex $argv 1]
set host [lindex $argv 0]
#set host $1
spawn ssh $user@$host

expect {
    "Connection refused" exit
    "Name or service not known" exit
    "continue connecting" {send "yes\r";exp_continue}
    "password:" {send "$pw\r";exp_continue}
    "Last login" {send "$cmd\nexit\n"}

}

expect eof
exit


