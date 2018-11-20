#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
from urllib import parse, request
from urllib.error import HTTPError
from base64 import urlsafe_b64encode
from time import sleep
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
import json

# Essa é a URL do servidor
api_url = 'https://vendingmachine075.herokuapp.com'
# Esse é o token que a vending machine vai usar para acessar o servidor
token = '308aaa205f81deafedfe802f3c44229562621dc6'
# Esse é o header que vai autenticar o pedido no servidor
header = {'Authorization': 'Token ' + token}

hash_RA = 0
RA = 0
def pegar_balanco(RA):
    """
    Função que recebe um RA e retorna o crédito
    que a pessoa tem

    Se conseguir pegar o crédito, retorna
    seu valor como um float
    Sennao, retorna o erro
    """
    encoded_RA = urlsafe_b64encode(RA.encode()).decode()
    url = api_url + '/balance/' + encoded_RA
    req = request.Request(url=url, headers=header)
    # Se o RA for inválido ou não existir no servidor, vai dar um erro aqui.
    # Vamos pegar esse erro e retornar None nesse caso
    try:
        response = request.urlopen(req)
        data = response.read().decode()
        # Retorna valor na conta
        return json.loads(data)['balance']
    except HTTPError:
        # RA é inválido ou não está salvo no servidor
        return 'RA inválido ou não cadastrado'


def efetuar_compra(RA, valor):
    print("aa")
    """
    Recebe um RA e valor e efetua uma compra
    em nome do usuário do RA com o valor informado

    Se tiver fundos, retorna 'Compra efetuada'
    Senão, retorna o erro
    """
    values = {
        'account': RA,
        'transaction': 'withdraw',
        'amount': valor
    }
    url = api_url + '/transactions/'
    data = parse.urlencode(values).encode()
    req = request.Request(url=url, data=data, headers=header)
    try:
        request.urlopen(req)
        # Se der certo, compra foi realizada com sucesso
        return 'Compra efetuada'
    except HTTPError as e:
        # Se deu erro, RA é inválido ou não registrado,	
        # ou o usuário não tem fundos suficientes
        error = json.loads(e.read().decode())
        if error.get('account', ['false'])[0] == 'account inválida':
            return 'RA inválido ou não cadastrado'
        return list(error.values())[0][0]

# a simple card observer that prints inserted/removed cards ATR
class PrintObserver(CardObserver):
	def update(self, observable, actions):
		global hash_RA
		(addedcards, removedcards) = actions
		for card in addedcards:
			hash_RA = toHexString(card.atr)
			saldo=pegar_balanco(hash_RA)
			print("Inserted: ", hash_RA)
			print("saldo: ",saldo)
			val = int(input("Selecione o produto\n"))
			if val == 1:
				print(efetuar_compra(hash_RA, 1.50))
			else:
				print("Produto indisponivel")
		for card in removedcards:
			print("Removed: ", toHexString(card.atr))

if __name__ == '__main__':
	cardmonitor = CardMonitor()
	cardobserver = PrintObserver()
	cardmonitor.addObserver(cardobserver)	
	#val = input("Digite 0 para sair\n")
	#if val == 0:
	sleep(100);
	cardmonitor.deleteObserver(cardobserver)
