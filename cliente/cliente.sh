#!/bin/bash
cd "$(dirname "$0")"
host=samuelkato.ddns.net
echo "aguardando conexao"
while ! ping -c 1 -W 1 8.8.8.8 >/dev/null  2>&1 ; do
	echo "."
	sleep 1
done
echo "Tem acesso a $host"
#tunel reverso para permitir acesso ssh à camera
autossh -R 2223:localhost:22 -N samuelkato@$host -p 2222 -i /home/pi/.ssh/rpiSoja -C < /dev/null &
wget --timeout=5 --tries=2 http://$host:3000/uploads/cliente.py -O clienteTmp.py > /dev/null 2>&1
wget --timeout=5 --tries=2 http://$host:3000/uploads/cliente.sh -O clienteTmp.sh > /dev/null 2>&1
#da erro caso nao tenha conseguido baixar
#dah pra fazer mta maldade com isso
if [ -s clienteTmp.sh ]; then
	mv clienteTmp.py cliente.py
	mv clienteTmp.sh cliente.sh
	chmod a+x cliente.py
	chmod a+x cliente.sh
else
	echo "sem acesso ao servidor"
	rm -f clienteTmp.*
fi

procID=$(pgrep -f "python3.*cliente.py")
if [[ $procID =~ ^-?[0-9]+$ ]] ; then
	kill $procID
fi

if ! pgrep -f "pigpiod" > /dev/null ; then
	sudo pigpiod
fi

#sudo -u pi { python3 cliente.py < /dev/null 2>erros.txt 1>saida.txt & }
sudo -u pi sh -c 'python3 cliente.py < /dev/null 2>erros.txt 1>saida.txt &'

exit 0
