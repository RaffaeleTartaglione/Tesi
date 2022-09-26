import random     


def genera_indirizzi(tipo_miss, size_max, dim_blocco, sets, ways, n_indirizzi):
    random_addresses = []
    sw = sets*ways
    valore_scelto = random.randint(1,size_max)
    min_int = int(valore_scelto/dim_blocco) * dim_blocco                        #calcolo intervallo di interesse (per valori possibili)
    max_int = min_int + dim_blocco
    val_ind1 = random.randint(min_int,max_int)                                  #calcolo valori random nell'intervallo
    val_ind2 = random.randint(min_int,max_int)

    distanza = random.randint(1, n_indirizzi)
    ind1 = random.randint(0, n_indirizzi - distanza)
    ind2 = ind1 + distanza - 1

    if tipo_miss == "cap":      #se accessi (distanza) > set*way
        if sw < n_indirizzi:
            distanza = random.randint(sw, n_indirizzi)
        else: distanza = n_indirizzi
        
        #distanza = random.randint(sw, n_indirizzi)
        ind1 = random.randint(0, n_indirizzi - distanza)
        ind2 = ind1 + distanza - 1

    elif tipo_miss == "conf":   #se accessi (distanza) <= set*way
        distanza = random.randint(1, sw+1)
        ind1 = random.randint(0, n_indirizzi - distanza)
        ind2 = ind1 + distanza - 1

    #print(ind1)
    #print(ind2)
    random_ways = ways + random.randint(0, distanza)                                #quante vie ho
    
    random_ripetizioni = random.randint(0, random_ways - ways)

    for i in range(n_indirizzi):
        if i == ind1:
            random_addresses.append(val_ind1)                                  #str solo per vedere in print
            #print(str(val_ind1))
        elif i == ind2:
            random_addresses.append(val_ind2)
            #print(str(val_ind2))
        ###elif ind1 < i < ind2:

        else:
            indirizzo = random.randint(1,size_max)                                  #seleziono valori che non danno fastidio ai due selezionati
            while min_int <= indirizzo <= max_int:
                indirizzo = random.randint(1,size_max)
            random_addresses.append(indirizzo)

    def sindex_dtag(valore_scelto, dim_blocco, sets):
        n_blocco = int(valore_scelto/dim_blocco)
        index = n_blocco % sets
        tag = int(n_blocco/sets)
        #trovare numero (indirizzo) con index uguale ma tag diverso
        trovato = False
        candidate = 0
        while not trovato:
            candidate = random.randint(1,size_max)
            n_blocco_cand = int(candidate/dim_blocco)
            if n_blocco_cand%sets == index and int(n_blocco_cand/sets) != tag:
                trovato = True
        return candidate

    #devo aggiungere in posizioni random, tante volte quante >= ways, quindi:
    #devo mettere indirizzo t.c. index stesso di indirizzi scelti ma tag diverso t.c. quantità >= ways
    # - ho i due indici che scandiscono l'intervallo e quanti elementi devo aggiungere
    # metto un contatore=random_ways
    indici_usati = []

    #if tipo_miss == "cap" or tipo_miss == "conf":
    while random_ways !=  0:
        #mettere controllo per non rischiare di prendere stesso indice (utile anche per le ripetizioni)
        pos_random = random.randint(ind1 + 1, ind2)     #PROBLEMA (forse togliere -1)
        while pos_random in indici_usati:
            pos_random = random.randint(ind1 + 1, ind2)
        random_addresses[pos_random] = sindex_dtag(valore_scelto, dim_blocco, sets)
        random_ways -= 1
        indici_usati.append(pos_random)

    #controllo len(indici_usati) < distanza?
    #controllo per ciclare max 10 volte?
    #prendere un valore di quelli già dentro l'intervallo (ind1 e ind2) [anche in indici_usati]
    #calcolare il valore random_value
    #metterlo in una posizione che non sia in indici_usati
    
    while random_ripetizioni != 0:
        pos_random = random.randint(ind1 + 1, ind2)     #PROBLEMA (forse togliere -1)

        while pos_random in indici_usati:
            pos_random = random.randint(ind1 + 1, ind2)                                 #prendo una posizione mai usata finora

        pos_indici_usati_random = indici_usati[random.randint(0, len(indici_usati))]    #prendo un indice già usato perchè così so che il valore non verrà mai modificato
        random_value = random_addresses[pos_indici_usati_random]                        #prendo il valore corrispondente
        #calcolare intervallo
        min_value = int(random_value/dim_blocco) * dim_blocco                           #mi calcolo l'intervallo del valore
        max_value = min_value + dim_blocco
        random_value = random.randint(min_value,max_value)                              #prendo un valore randomico in quest'intervallo
        random_addresses[pos_random] = random_value         #PRENDERE NUMERO CHE SI TROVA GIà NELL'INTERVALLO E USARNE UNO NEL SUO INTERVALLO DI VALORI CON STESSO #BLOCCO
        random_ripetizioni -= 1
        indici_usati.append(pos_random)

    #controllo indirizzi con stesso #blocco (ripetizioni)

    print(random_addresses)
    #print(distanza)
    print(ind1)
    print(ind2)
    
    return random_addresses, distanza, ind1, ind2