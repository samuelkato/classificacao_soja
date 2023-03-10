# classificacao_soja
sistema para avaliar qualidade da soja

- cliente:
  - cameras rpi mandando fotos pra um servidor através do código cliente.py
  - colocar ID no cliente para que varios clientes possam rodar simulaneamente OK
	- timer após desligar o coletor de amostras
	- hora OK
	- umidade 
		- calibrar com dados reais
	- foto OK
		- hq cam + lente com zoom variavel
		- camera v2 ou v1.3 (foco mto dificil de setar)
	- enviar dados para o servidor externo ou gravar localmente (zip?)
		- buffer para ser enviado qdo houver internet OK
	- destravar caixa OK
	- atualizacao automatica OK
- servidor:
	- receber foto e outros dados do rpi OK
	- pesquisar dados em um sistema externo
	- comparar dados
	- produzir relatorio em email
	- interface para gerenciamento interno?
		- listagem para diagnostico OK
		- login
		- escolha de fotos para novo treinamento
		- permitir criação e remoção de classificações pela interface
	- comunicacao segura entre o servidor e o cliente
  - classificação automática da foto feita com keras e tensorflow
  	- código de aprendizado de máquina basedo no seguinte exemplo:
  		- https://pyimagesearch.com/2017/12/11/image-classification-with-keras-and-deep-learning/
	- guardar fotos em pasta msm OK
		- como gerar nome unico para as imagens
	- aguardando dados reais para recriar o classificador
	
	
