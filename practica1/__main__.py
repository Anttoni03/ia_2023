from practica1 import agent, joc


def main():
    player1 = agent.Agent("A")
    player2 = agent.Agent("B")
    if agent.TIPUS_CERCA == 3:
        quatre = joc.Taulell([player1, player2])
    else:
        quatre = joc.Taulell([player1])
    quatre.comencar()


if __name__ == "__main__":
    main()
