from practica1 import agent, joc


def main():
    player1 = agent.Agent("Miquel")
    player2 = agent.Agent("Toni")
    if agent.TWO_PLAYERS:
        quatre = joc.Taulell([player1, player2])
    else:
        quatre = joc.Taulell([player1])
    quatre.comencar()


if __name__ == "__main__":
    main()
