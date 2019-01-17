#/bin/bash
EXPECTED_ARGS=1

if [ $# -ne $EXPECTED_ARGS ]
then
        printf  "\nYou need to provide the entry point for the debugger\nExample:\n./debug.sh test.py\n"
else
        echo "[+] Waiting for debugger attachment."
        python3 -m ptvsd --host 0.0.0.0 --port 3000 --wait $1
fi;
