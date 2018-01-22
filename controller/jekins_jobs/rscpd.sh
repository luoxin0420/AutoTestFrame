#!/usr/bin/expect
set timeout 5

#set pw $2
set desfolder [lindex $argv 4]
set srcfolder [lindex $argv 3]
set pw [lindex $argv 2]
set user [lindex $argv 1]
set host [lindex $argv 0]
#set host $1
spawn scp -r $user@$host:$srcfolder $desfolder

expect {
    "Connection refused" {exit}
    "Name or service not known" {exit}
    "continue connecting"{send "yes\r"}
    "password:" {send "$pw\r"; exp_continue}
}

expect eof
exit


