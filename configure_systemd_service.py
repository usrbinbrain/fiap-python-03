#!/usr/bin/env python3
import subprocess
import sys
import os

### Variavel contem o caminho absoluto do diretorio de configuracao dos servicos do systemd.
DIRETORIO_SERVICO_SYSTEMD = '/etc/systemd/system/'

### Variavel contem o comando Linux que verifica a existencia do systemd e o diretorio de instalacao dos arquivos de configuracao dos servicos.
COMANDO_VALIDACAO_SYSTEMD = f'systemd --version && ls {DIRETORIO_SERVICO_SYSTEMD}'

### Funcao para criacao de configuracao do servico no systemd.
def configure_o_servico_systemd(caminho, nome, config, usuario_execucao):
    """ 
        Esta funcao opera com os seguintes parametros:

        'caminho' -> Recebe o caminho absoluto do script no S.O.
        'nome'    -> Recebe o nome do servico extraido do nome do script.
        'config'  -> Recebe o caminho do arquivo de configyracao do servico no systemd.
        'usuario_execucao' -> Recebe o nome de usuario (S.O) que vai executar o servico.
    """

    ### Adiciona permissao de execucao no caminho absoluto valido.
    subprocess.run(['chmod', '+x', caminho], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ### Variavel contem o template de configuracao de um servico no systemd.
    TEMPLATE_CONFIGURACAO = "[Unit]\n"\
    f"Description=Servico {nome} (configurado via script python).\n"\
    "After=network.target\n"\
    "StartLimitIntervalSec=0\n\n"\
    "[Service]\n"\
    "Type=simple\n"\
    "Restart=always\n"\
    "RestartSec=1\n"\
    f"User={usuario_execucao}\n"\
    f"ExecStart={caminho}\n\n"\
    "NoNewPrivileges=yes\n"\
    "ProtectSystem=strict\n"\
    "LockPersonality=yes\n"\
    "ProtectClock=yes\n"\
    "ProtectHostname=yes\n"\
    "ProtectControlGroups=yes\n\n"\
    "ProtectKernelModules=yes\n"\
    "ProtectKernelTunables=yes\n"\
    "RestrictSUIDSGID=yes\n\n"\
    "[Install]\n"\
    "WantedBy=multi-user.target\n"
    
    ### Criando o arquivo de configuuracao do servico no systemd.
    with open(config, "w+") as conf:
        conf.write(TEMPLATE_CONFIGURACAO)
    ### Imprimindo informacoes de deploy do servico.
    print(f"[+] O servico '{nome}' foi configurado com exito no systemd do S.O.")
    print(f"[+] Execute os seguintes comando para recarregar o systemd e iniciar o servico '{nome}'.")
    print(f"[$] systemctl daemon-reload && systemctl enable --now {nome}")
    
### Identifica se o systemd existe no sistema operacional.
try:
    #### Tenta identificar se existe o systemd no S.O.
    resultado_comando = subprocess.run(COMANDO_VALIDACAO_SYSTEMD.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #### Imprima esse padrao de texto.
    #print("[+] O systemd foi identificado!")

### Caso nao exista systemd no S.O.
except FileNotFoundError:
    print("[!] O systemd nao foi identificado nesse S.O.")
    #### Encerre a execucao do script
    exit()

### Identifica se existe argumento na execucao do script.
if len(sys.argv) > 1:
    #### Variavel recebe o caminho absoluto passado como argumento.
    caminho_do_arquivo = sys.argv[1]

    #### Se o primeiro caracter do argumento passado nao for "/", indicando um caminho absoluto invalido.
    if not caminho_do_arquivo[:1] == "/":
        print(f"[!] O caminho absoluto deve ser valido, por exemplo: {sys.argv[0]} /root/exemplo_script.py")
        ###### Encerre a execucao do script
        exit()

    #### Se o primeiro caracter do argumento passado for "/", indicando um caminho absoluto valido.
    else:   
        #### Variavel recebe o nome do script presente no caminho absoluto.
        nome_do_script = caminho_do_arquivo.split("/")[-1:][0]
        #### Variavel recebe o nome do usuario Linux que esta executando o script python.
        nome_do_usuario = os.environ.get('USER')

        #### Tente extrair o nome do servico do nome do script removendo a estensao do script.
        try:
            ##### Variavel recebe o nome do script sem a estensao.
            nome_do_servico = nome_do_script.split(".")[:-1][0]
            ##### Variavel recebe o caminho absoluto do arquivo de configuracao do servico no systemd.
            caminho_do_arquivo_service = f"{DIRETORIO_SERVICO_SYSTEMD}{nome_do_servico}.service"

        #### Caso o nome do script nao tenha extensao.
        except IndexError:
            ##### Imprima esse padrao de texto.
            print("[!] O nome do script deve conter uma externsao, exemplo : /root/script.py")
            ##### Encerre a execucao do script
            exit()

        ##### Exibe um padrao de texto contendo o caminho absoluto valido.
        print(f"[+] O argumento passado foi : {sys.argv[1]}, o nome do script : {nome_do_script}")

        ##### Verifica se o script passado como argumento ja esta configurado como servico no S.O.
        if os.path.isfile(caminho_do_arquivo_service):

            ###### Imprime o seguinte padrao de texto.
            print(f"[?] Ja existe um servico ({nome_do_servico}) configurado com o script {nome_do_script}!")
            resposta_atualizacao = str(input(f"[?] Deseja atualizar o servico ({nome_do_servico}) com o script {caminho_do_arquivo}? (sim/nao): "))

            ###### Se a resposta do operador do script for sim.
            if resposta_atualizacao.lower() == "sim":

                ####### Realize o deploy da configuracao do servico.
                configure_o_servico_systemd(caminho_do_arquivo, nome_do_servico, caminho_do_arquivo_service, nome_do_usuario)

            ###### Se a resposta for qualquer outra coisa alem de 'sim'.
            else:

                ####### Informe que nada foi alterado no S.O.
                print("[!] Nenhuma modificacao foi realizada!")
                ####### Encerre a execucao do script
                exit()

        ##### Caso o script nao estaja configurado no S.O.
        else:
            
            ######## Faca o deploy da configuracao.
            configure_o_servico_systemd(caminho_do_arquivo, nome_do_servico, caminho_do_arquivo_service, nome_do_usuario)

### Caso nao exista argumento na execucao do script.
else:
    #### Imprima esse padrao de texto.
    print("[!] Nao existe um argumento no script, informe o caminho absoluto do seu script.")
    #### Encerre a execucao do script
    exit()
