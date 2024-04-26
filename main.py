import datetime

AGENCIA = "0001"
LIMITE_DIARIO = 500
LIMITE_SAQUES = 3
LIMITE_TRANSACOES_DIARIAS = 10
clientes = []

class Endereco:
    def __init__(self, rua, numero, complemento, bairro, cidade, uf):
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf

class Cliente:
    def __init__(self, cpf, nome, data_nascimento, endereco, qtd_saques=0):
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.endereco = endereco
        self.contas = []
        self.qtd_saques = qtd_saques
        self.index = 0

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.contas):
            result = self.contas[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

class Transacao:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
        self.horario = datetime.datetime.now()

    def registrar(self, conta):
        conta.extrato.append((self.horario, self.valor))

class Conta:
    def __init__(self, cliente, numero_conta, agencia, extrato=None):
        self.cliente = cliente
        self.numero_conta = numero_conta
        self.agencia = agencia
        if extrato is None:
            self.extrato = []
        else:
            self.extrato = extrato
        self.historico = Historico()  # Cria uma instância de Historico para a conta

    def realizar_transacao(self, transacao):
        transacao.registrar(self)

    @property
    def saldo(self):
        total = 0
        for horario, valor in self.extrato:
            total += valor
        return total

    def efetiva_deposito(self, valor):
        if valor > 0:
            now = datetime.datetime.now()
            self.extrato.append((now, valor))  # Adiciona uma tupla (horário, valor) ao extrato
            self.historico.registrar_transacao("Depósito", valor, now)
            return True
        else:
            print('Valor não pode ser negativo')
            return False

    def efetiva_retirada(self, valor):
        if self.cliente.qtd_saques > LIMITE_SAQUES:
            print(f'Valor excede limite de saque. Limite: R$ {self.cliente.qtd_saques}')
            return False
        elif valor > self.saldo:
            print('Saldo insuficiente para saque.')
            return False
        else:
            now = datetime.datetime.now()
            self.extrato.append((now, -valor))  # Adiciona uma tupla (horário, valor) ao extrato
            self.historico.registrar_transacao("Saque", valor, now)
            return True

    def listar_extrato(self):
        if not self.extrato:
            print('Não foram realizadas movimentações!')
        else:
            print("==========================================")
            print(f"CPF: {self.cliente.cpf}")
            print(f"Agência: {self.agencia}")
            print(f"C/C: {self.numero_conta}")
            print(f"Titular: {self.cliente.nome}")
            print("==========================================")
            print("Início Extrato")
            for horario, valor in self.extrato:
                if valor >= 0:
                    print(f"Depósito: {valor}, Horário: {horario}")
                else:
                    print(f"Saque: {-valor}, Horário: {horario}")
            print(f"\nSaldo: R$ {self.saldo}")
            print("Fim Extrato")
            print("==========================================")

class Historico:
    def __init__(self):
        self.transacoes = []

    def registrar_transacao(self, tipo, valor, horario):
        self.transacoes.append((tipo, valor, horario))

    def mostrar_transacoes(self):
        print("Histórico de Transações:")
        for tipo, valor, horario in self.transacoes:
            print(f"Tipo: {tipo}, Valor: {valor}, Horário: {horario}")

def retira_sinais(texto):
    resultado = ''
    for caractere in texto:
        if caractere.isdigit():
            resultado += caractere
    return resultado

def menu_conta():
    tela = """
            Movimentação de Conta Corrente

                Selecione uma opção:
                [C]adastrar Cliente
                [I]ncluir Conta
                [P]osicionar Cliente/Conta
                [L]istar Contas

                [S]air
        => """
    return input(tela)

def menu_opcoes():
    tela = """
            Movimentação de Conta Corrente

                Selecione uma opção:
                [D]epositar
                [R]etirar
                [E]xtrato
                [T]ransações

                [V]oltar
        => """
    return input(tela)

def saldo_conta(conta):
    return sum(valor for _, valor in conta.extrato)

def selecionar_cliente(cpf):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def selecionar_conta(cpf, numero_conta):
    cliente = selecionar_cliente(cpf)
    if cliente:
        for conta in cliente.contas:
            if conta.numero_conta == numero_conta:
                return conta
    return None

def listar_contas():
    print("==========================================")
    print("Início da Listagem")
    for cliente in clientes:
        for conta in cliente.contas:
            saldo = conta.saldo
            print(f"""
                Agência: {conta.agencia}
                C/C: {conta.numero_conta}
                Titular: {cliente.nome}
                Saldo: {saldo}
            """)
    print("Fim da Listagem")
    print("==========================================")

def criar_conta(cliente):
    if cliente:
        numero_conta = len(cliente.contas) + 1
        conta = Conta(cliente, numero_conta, AGENCIA)
        cliente.adicionar_conta(conta)
        return conta
    else:
        print("Cliente não cadastrado!")

def solicitar_numero_conta():
    while True:
        numero_conta = input("Número da conta: ")
        if numero_conta.isdigit():
            return int(numero_conta)
        else:
            print("Por favor, insira apenas números inteiros para o número da conta.")

def depositar(conta):
    valor = float(input("Entre com o valor do depósito: "))
    if valor > 0:
        conta.efetiva_deposito(valor)
    else:
        print('Valor não pode ser negativo')

def retirar(numero_saques, conta):
    if numero_saques >= LIMITE_SAQUES:
        print(f'Limite de saques diários atingido (Máximo {LIMITE_SAQUES})')
    else:
        valor = float(input("Entre com o valor de saque: "))
        if valor < 0:
            print('Valor não pode ser negativo')
        else:
            if conta.efetiva_retirada(valor):
                numero_saques += 1

def listar_transacoes(conta):
    conta.historico.mostrar_transacoes()

while True:
    opcao = menu_conta().upper()

    if opcao == 'C':
        cpf = input("CPF: ")
        nome = input("Nome: ")
        data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
        rua = input("Rua: ")
        numero = input("Número: ")
        complemento = input("Complemento: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        uf = input("UF: ")
        endereco = Endereco(rua, numero, complemento, bairro, cidade, uf)
        clientes.append(Cliente(cpf, nome, data_nascimento, endereco))
        print("Cliente cadastrado com sucesso!")

    elif opcao == 'I':
        cpf = input("CPF do cliente: ")
        cliente = selecionar_cliente(cpf)
        conta = criar_conta(cliente)
        if conta:
            print("Conta cadastrada com sucesso!")

    elif opcao == 'L':
        listar_contas()

    elif opcao == 'P':
        cpf = input("CPF do cliente: ")
        numero_conta = solicitar_numero_conta()
        conta = selecionar_conta(cpf, numero_conta)
        
        opcao_conta = ''
        numero_transacoes = 0
        numero_saques = 0
        while opcao_conta != 'V':
            opcao_conta = menu_opcoes().upper()
            if opcao_conta == 'D':
                depositar(conta)
            elif opcao_conta == 'R':
                retirar(numero_saques, conta)
            elif opcao_conta == 'E':                
                conta.listar_extrato()
            elif opcao_conta == 'T':
                listar_transacoes(conta)
            elif opcao_conta == 'V':
                break
            else:
                print("Opção inválida!")

    elif opcao == 'S':
        break

    else:
        print("Opção inválida!")
