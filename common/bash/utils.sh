#!/bin/bash

# Trap for SIGUSR1
trap "exit 1" USR1
PROC_ID=$$

# Exit script from a subshell
exit_all () {
  kill -USR1 "$PROC_ID"
}

# Colors
COLOR_BLACK='\033[0;30m'  ; COLOR_DGRAY='\033[1;30m'
COLOR_RED='\033[0;31m'    ; COLOR_LRED='\033[1;31m'
COLOR_GREEN='\033[0;32m'  ; COLOR_LGREEN='\033[1;32m'
COLOR_BROWN='\033[0;33m'  ; COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'   ; COLOR_LBLUE='\033[1;34m'
COLOR_PURPLE='\033[0;35m' ; COLOR_LPURPLE='\033[1;35m'
COLOR_CYAN='\033[0;36m'   ; COLOR_LCYAN='\033[1;36m'
COLOR_LGRAY='\033[0;37m'  ; COLOR_WHITE='\033[1;37m'
UNDERLINE="\e[4m"
UL="$UNDERLINE"
FORMAT_RESET='\033[0m'
FR="$FORMAT_RESET"

echo_usage () {
  echo -e "$COLOR_GREEN""Usage:""$FORMAT_RESET"  >&2
  echo -e "$(usage | grep -v 'Usage:' )"  >&2
}

usage () {
  echo "Usage stub"
}

header () {
  echo " "
  echo -e "$COLOR_CYAN""-== $* | $(date) ==-""$FORMAT_RESET"
}

error_echo () {
  echo -e "$COLOR_RED""Error:""$FORMAT_RESET" >&2
  echo " $*" >&2
  echo " " >&2
}

check_arg_num () {
  if [ "$1" != "$2" ]
  then
    error_echo "Wrong number of command line arguments!"
    usage
    exit 1
  fi
}

check_arg_is_int () {
  re='^[0-9]+$'
  if ! [[ $1 =~ $re ]] ; then
   error_echo "$1 is not an integer"
   usage
   exit 1
  fi
}

check_arg_is_dir () {
  if [ ! -d "$1" ]
  then
    error_echo "$1 is not an existing directory"
    usage
    exit 1
  fi
}

check_arg_is_file () {
  if [ ! -f "$1" ]
  then
    error_echo "$1 is not an existing file"
    usage
    exit 1
  fi
}

# More convenient functions
arg_num () {
  # $1 - wanted number of arguments
  # $2 - correct number of arguments
  if [ "$1" != "$2" ]
  then
    error_echo "$1 is wrong number of arguments! This script takes $2"
    echo_usage
    exit_all
  fi
}

arg_is_pos_int () {
  re='^[0-9]+$'
  if ! [[ $1 =~ $re ]] ; then
   error_echo "'$1' is not an integer"
   echo_usage
   exit_all
  fi
  echo "$1"
}

arg_is_dir () {
  if [ ! -d "$1" ]
  then
    error_echo "'$1' is not a directory"
    echo_usage
    exit_all
  fi
  echo "$1"
}

arg_is_file () {
  if [ ! -f "$1" ]
  then
    error_echo "'$1' is not a file"
    echo_usage
    exit_all
  fi
  echo "$1"
}