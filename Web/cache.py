import fasi

class Cache():

    def __init__(self, addresses, cache_type, data_type, data_dim, sets, ways, lvl, offset, init, lvlinit):  #DA COMPLETARE
        self.addresses = addresses
        self.cache_type = cache_type
        self.data_type = data_type
        self.data_dim = data_dim
        self.sets = sets
        self.ways = ways
        self.lvl = lvl
        self.data = None
        self.offset = offset
        self.init = init
        self.lvlinit = lvlinit
        
        self.fin = None
   
    def get_addresses(self):
        return self.addresses
    def get_cache_type(self):
        return self.cache_type
    def get_data_type(self):
        return self.data_type
    def get_data_dim(self):
        return self.data_dim
    def get_sets(self):
        return self.sets
    def get_ways(self):
        return self.ways
    def get_lvl(self):
        return self.lvl
    def get_offset(self):
        return self.offset
    def get_init(self):
        return self.init
    def get_lvlinit(self):
        return self.lvlinit
    

    def riempicache(cache_table):

        def dim_blocco(tipo_dato, dim_indirizzo):
        #if word, halfword etc
            return tipo_dato*dim_indirizzo

        # 1120 545 129 1099 1100 2056 319 445 2060 538 131 318 130 528

        # 2048 3072 4096 6144 8192 12288 16384 24576 49152 73728 98304 147456 98389

        #addresses = [1120, 545, 129, 1099, 1100, 2056, 319, 445, 2060, 538, 131, 318, 130, 528]     #PER ORA SOVRASCRIVE    (es 6)

        #addresses = [27, 330, 123, 333, 155, 91, 126, 190, 107, 95, 331, 812, 163]          #       (es 2)

        #addresses = [2048, 3072, 4096, 6144, 8192, 12288, 16384, 24576, 49152, 73728, 98304, 147456, 98389]    #es. cache iniziale

        addresses = cache_table.get_addresses()
       
        cache_table.data = [[[fasi.Stage() for i in addresses] for f in range(5+int(cache_table.get_offset()))] for l in range(cache_table.get_lvl())]
        data = cache_table.data
        #per livello: tipo dato, dim indirizzo, n_set, n_way
        #info_lvl = [[4, 4, 8, 2], [4, 16, 4, 1]]  #da input   (es 6)

        #info_lvl = [[4, 2, 4, 2], [4, 16, 2, 4]]           # (es 2)

        #info_lvl = [[4, 1024, 8, 1], [4, 2048, 1, 16]]     #es. cache iniziale

        #tipo_cache = [tipo1, tipo2] poi funziona con l'indice l

    #fully associative -> 1 set
    #direct mapped     -> 1 way
        init = cache_table.get_init()
        stor_init = {k:v for k,v in init.items()}

        for l in range(cache_table.get_lvl()):
            for i in range(len(addresses)):
                for f in range(5+int(cache_table.get_offset())):
                    # caso in cui nel livello precedente c'è stata una HIT -> " "
                    if l > 0 and data[l-1][3][i].get_value() == "H":
                        data[l][f][i].set_value(" ")

                    else:
                        if f == 0:
                            data[l][0][i] = fasi.BlockNumber(addresses[i], dim_blocco(cache_table.get_data_type()[l], cache_table.get_data_dim()[l]))
                        elif f == 1:
                            if cache_table.get_cache_type()[l] == "fully_associative": data[l][1][i] = data[l][0][i]
                            else: data[l][1][i] = fasi.Index(data[l][0][i].get_value(), cache_table.get_sets()[l])
                        elif f == 2:
                            if cache_table.get_cache_type()[l] == "fully_associative": data[l][2][i] = data[l][0][i]
                            else: data[l][2][i] = fasi.Tag(data[l][0][i].get_value(), cache_table.get_sets()[l])
                        elif f == 3:
                            data[l][3][i] = fasi.HM("M")
                        elif f == 5:
                            data[l][5][i] = fasi.Offset(addresses[i], dim_blocco(cache_table.get_data_type()[l], cache_table.get_data_dim()[l]))
                        elif f == 4:
                            if data[l][0][i].get_value() not in [x.get_value() for x in data[l][0][:i]] and (init == {} or cache_table.get_lvlinit() - 1 != l):
                                data[l][4][i] = fasi.TipoMiss("L")

                            #PROBLEMA "ELIF"
                            elif init != {} and cache_table.get_lvlinit() - 1 == l: #and init[data[l][1][i].get_value()] != str(data[l][2][i].get_value()):
                                """
                                - se init[index] != tag: L
                                - se init[index] != tag MA PRIMA init[index] == tag: cap o conf
                                - altrimenti: H
                                """

                                """
                                PER SISTEMARE INIT (se necessario):
                                - modificare tabella cache init input in pagine web (tag in base al nway + lru?)
                                - modificare controllo [-1] ed estenderlo a "[-ways]" -> for
                                - PROBLEMA -> non sempre valido append perchè potrebbe dover essere sostituito ultimo anzichè penultimo -> giocare con indici?
                                """

                                if str(data[l][2][i].get_value()) not in stor_init[data[l][1][i].get_value()]:
                                    stor_init[data[l][1][i].get_value()].append(str(data[l][2][i].get_value()))

                                    #PROBLEMA (devo controllare storico)
                                    data[l][4][i] = fasi.TipoMiss("L")
                                
                                elif str(data[l][2][i].get_value()) in stor_init[data[l][1][i].get_value()] and str(data[l][2][i].get_value()) not in stor_init[data[l][1][i].get_value()][-cache_table.get_ways()[l]:]:
                                    stor_init[data[l][1][i].get_value()].append(str(data[l][2][i].get_value()))
                                    #data[l][4][i] = fasi.TipoMiss("OH YEEEEAH")
                                    #parte else: n_way ...

                                    n_way = cache_table.get_ways()[l]
                                    #forse soluzione al problema -> incontri
                                    incontri = []

                                    for j in range(i-1,-1,-1):
                                        if data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() != data[l][2][i].get_value() and data[l][2][j].get_value() not in incontri:
                                            n_way -= 1
                                            incontri.append(data[l][2][j].get_value())

                                        if n_way <= 0 and cache_table.get_lvlinit() - 1 == l and (j) == 0 and data[l][0][j].get_value() != data[l][0][i].get_value():   #dobbiamo capire se è miss di cap o di conf
                                            
                                            #PROBLEMA
                                            continit = 0
                                            #calcolo indice massimo cache iniziale CON valore
                                            #dict.keys()[-1]
                                            ind_max = -1
                                            trovato = False
                                            while not trovato or ind_max*(-1) == len(init):
                                                if "" not in init[list(init.keys())[ind_max]]:
                                                    trovato = True
                                                else:
                                                    ind_max -= 1
                                            #(indice max init - indice per cui #blocco è uguale)
                                            for k,v in init.items():
                                                for t in v:
                                                    if t != "":
                                                        if int(t)*cache_table.get_sets()[l]+k == data[l][0][i].get_value():
                                                            continit = len(init) + ind_max - k      # indice max di init - indice max effettivo (non "") - indice di interesse (riscontro)
                                            
                                            #diff = (i - j - vuoti - (len([x.get_value() for x in data[l][0][j:i]]) - len(set([x.get_value() for x in data[l][0][j:i]]))))
                                            ins = set([x.get_value() for x  in data[l][0][j:i] if x.get_value() != " "])
                                            diff  = len(ins) + continit
                                            if (diff <=  cache_table.get_sets()[l] * cache_table.get_ways()[l]):
                                                data[l][4][i].set_value("Conf.")
                                            else:
                                                data[l][4][i].set_value("Cap.")
                                            break

                                        elif data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() == data[l][2][i].get_value() and n_way > 0:
                                            data[l][3][i].set_value("H")
                                            data[l][4][i].set_value(" ")
                                            break

                                        elif n_way <= 0 and (data[l][0][j].get_value() == data[l][0][i].get_value()):   #dobbiamo capire se è miss di cap o di conf
                                            #diff = (i - j - vuoti - (len([x.get_value() for x in data[l][0][j:i]]) - len(set([x.get_value() for x in data[l][0][j:i]]))))
                                            ins = set([x.get_value() for x  in data[l][0][j:i] if x.get_value() != " "])
                                            diff  = len(ins)
                                            if (diff <=  cache_table.get_sets()[l] * cache_table.get_ways()[l]):
                                                data[l][4][i].set_value("Conf.")
                                            else:
                                                data[l][4][i].set_value("Cap.")
                                            break

                                else:
                                    data[l][3][i] = fasi.TipoMiss("H")
                                    data[l][4][i] = fasi.TipoMiss(" ")
                            
                            else:
                                n_way = cache_table.get_ways()[l]
                                #forse soluzione al problema -> incontri
                                incontri = []

                                for j in range(i-1,-1,-1):
                                    if data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() != data[l][2][i].get_value() and data[l][2][j].get_value() not in incontri:
                                        n_way -= 1
                                        incontri.append(data[l][2][j].get_value())

                                    elif data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() == data[l][2][i].get_value() and n_way > 0:
                                        data[l][3][i].set_value("H")
                                        data[l][4][i].set_value(" ")
                                        break

                                    elif n_way <= 0 and (data[l][0][j].get_value() == data[l][0][i].get_value()):   #dobbiamo capire se è miss di cap o di conf
                                        #diff = (i - j - vuoti - (len([x.get_value() for x in data[l][0][j:i]]) - len(set([x.get_value() for x in data[l][0][j:i]]))))
                                        ins = set([x.get_value() for x  in data[l][0][j:i] if x.get_value() != " "])
                                        diff  = len(ins)
                                        if (diff <=  cache_table.get_sets()[l] * cache_table.get_ways()[l]):
                                            data[l][4][i].set_value("Conf.")
                                        else:
                                            data[l][4][i].set_value("Cap.")
                                        break
        #if lvlinit != 0:
        #calcolo la cache finale (fin)

        if cache_table.get_lvlinit() != 0:
            cachef = dict()
            init_index_order = list(cache_table.get_init().keys())
            ways = cache_table.get_ways()[cache_table.get_lvlinit()-1]
            for index in init_index_order:
                tags = stor_init[index][-ways:]
                cachef[index] = tags
            #controllo se ci sono elementi presenti nella cache iniziale non "sfruttati"
            for k,v in cache_table.get_init().items():
                if k not in cachef:
                    cachef[k] = v

            cachef = [[k]+v for k,v in cachef.items()]
            cache_table.fin = cachef


    """
    (lvlinit == l and init[data[l][1][i].get_value()] == data[l][2][i].get_value()))

    elif n_way == 0:   #dobbiamo capire se è miss di cap o di conf

        if cache_table.get_lvlinit() != 0 and (i - j - 1) == 0:
        continit = 0
        if lvlinit == l:    #(indice max init - indice per cui #blocco è uguale)
            for k,v in init.items():        però lista
                if v*info_lvl[l][2]+k == data[l][0][i].get_value():
                    continit = max(init) - k

    ... vuoti - ripetizioni - continit ...
    """
    """
    PER IL CASO CON CACHE INIZIALE:
    All'inizio controllo se ho già incontrato il numero di blocco o se il (index,tag) è già nella cache
    - se sì allora HIT
    - se no allora MISS
    Quando vado a vedere di che tipo di MISS abbiamo:
    - se prima volta che incontriamo il numero di blocco allora L
    - altrimenti:
        * considero il numero delle vie e procedo a ritroso
        * se trovo lo stesso index ma tag uguale -> decremento il numero di vie di 1
        * se trovo lo stesso index e lo stesso tag e il numero di vie è maggiore di 0 -> HIT
        * se il numero di vie è uguale a zero allora:
            - se la distanza accessi allo stesso numero di blocco è maggiore di vie*set (no vuoti e ripetizioni) incluso quello in init (a ritroso) -> Cap.
            - altrimenti Conf.

    Per calcolare lo stato finale della cache bisogna andare indietro negli accessi
    """

    def correggi(cache_table, data_utente, tabf, changed_cells=None):

        #addresses = [1120, 545, 129, 1099, 1100, 2056, 319, 445, 2060, 538, 131, 318, 130, 528]     #PER ORA SOVRASCRIVE    (es 6)

        addresses = cache_table.get_addresses()[1:]

        info_lvl = [[4, 4, 8, 2], [4, 16, 4, 1]]  #da input   (es 6)

        def dim_blocco(tipo_dato, dim_indirizzo):
        #if word, halfword etc
            return tipo_dato*dim_indirizzo

        errori = 0
        commenti = []

        cache_table.data = [[[fasi.Stage() for i in addresses] for i in range(5+int(cache_table.get_offset()))] for l in range(cache_table.get_lvl())]
        data = cache_table.data

        init = cache_table.get_init()
        stor_init = {str(k):v for k,v in init.items()}
        print(init)
        print(stor_init)

        indici_errori = []

        for l in range(cache_table.get_lvl()):
            for i in range(len(addresses)):
                for f in range(5+int(cache_table.get_offset())):
                    # caso in cui nel livello precedente c'è stata una HIT -> " "
                    if l > 0 and data[l-1][3][i].get_value() == "H":
                        data[l][f][i].set_value("")

                    else:
                        if f == 0:
                            data[l][0][i] = fasi.BlockNumber(addresses[i], dim_blocco(cache_table.get_data_type()[l], cache_table.get_data_dim()[l]))
                        elif f == 1: 
                            if cache_table.get_cache_type()[l] == "fully_associative": data[l][1][i] = data[l][0][i]
                            else: data[l][1][i] = fasi.Index(data[l][0][i].get_value(), cache_table.get_sets()[l])
                        elif f == 2:
                            if cache_table.get_cache_type()[l] == "fully_associative": data[l][2][i] = data[l][0][i]
                            else: data[l][2][i] = fasi.Tag(data[l][0][i].get_value(), cache_table.get_sets()[l])
                        elif f == 3:
                            data[l][3][i] = fasi.HM("M")
                        elif f == 5:
                            data[l][5][i] = fasi.Offset(addresses[i], dim_blocco(cache_table.get_data_type()[l], cache_table.get_data_dim()[l]))
                        elif f == 4:
                            if data[l][0][i].get_value() not in [x.get_value() for x in data[l][0][:i]] and (init == {} or cache_table.get_lvlinit() - 1 != l):
                                data[l][4][i] = fasi.TipoMiss("L")

                            #PROBLEMA "ELIF"
                            elif init != {} and cache_table.get_lvlinit() - 1 == l: #and init[data[l][1][i].get_value()] != str(data[l][2][i].get_value()):
                                """
                                - se init[index] != tag: L
                                - se init[index] != tag MA PRIMA init[index] == tag: cap o conf
                                - altrimenti: H
                                """
                                if str(data[l][2][i].get_value()) not in stor_init[str(data[l][1][i].get_value())]:
                                    stor_init[str(data[l][1][i].get_value())].append(str(data[l][2][i].get_value()))

                                    #PROBLEMA (devo controllare storico)
                                    data[l][4][i] = fasi.TipoMiss("L")
                                
                                elif str(data[l][2][i].get_value()) in stor_init[str(data[l][1][i].get_value())] and str(data[l][2][i].get_value()) not in stor_init[str(data[l][1][i].get_value())][-cache_table.get_ways()[l]:]:
                                    stor_init[str(data[l][1][i].get_value())].append(str(data[l][2][i].get_value()))
                                    #data[l][4][i] = fasi.TipoMiss("OH YEEEEAH")
                                    #parte else: n_way ...

                                    n_way = cache_table.get_ways()[l]
                                    #forse soluzione al problema -> incontri
                                    incontri = []
                                    for j in range(i-1,-1,-1):
                                        if data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() != data[l][2][i].get_value() and data[l][2][j].get_value() not in incontri:

                                            n_way -= 1
                                            incontri.append(data[l][2][j].get_value())

                                        if n_way <= 0 and cache_table.get_lvlinit() - 1 == l and j == 0 and data[l][0][j].get_value() != data[l][0][i].get_value():   #dobbiamo capire se è miss di cap o di conf
                                            
                                            #PROBLEMA
                                            continit = 0
                                            #calcolo indice massimo cache iniziale CON valore -> però dovrei prendere l'ultimo
                                            ind_max = -1
                                            trovato = False
                                            while not trovato or ind_max*(-1) == len(init):
                                                if "" not in init[list(init.keys())[ind_max]]:
                                                    trovato = True
                                                else:
                                                    ind_max -= 1
                                            #(indice max init - indice per cui #blocco è uguale)
                                            for k,v in init.items():
                                                for t in v:
                                                    if t != "":
                                                        print(int(t)*cache_table.get_sets()[l]+k, data[l][0][i].get_value())
                                                        if int(t)*cache_table.get_sets()[l]+k == data[l][0][i].get_value():
                                                            continit = len(init) + ind_max - k      # indice max di init - indice max effettivo (non "") - indice di interesse (riscontro)
                                            
                                            #diff = (i - j - vuoti - (len([x.get_value() for x in data[l][0][j:i]]) - len(set([x.get_value() for x in data[l][0][j:i]]))))
                                            ins = set([x.get_value() for x  in data[l][0][j:i] if x.get_value() != ""])
                                            diff  = len(ins) + continit
                                            if (diff <=  cache_table.get_sets()[l] * cache_table.get_ways()[l]):
                                                data[l][4][i].set_value("Conf.")
                                            else:
                                                data[l][4][i].set_value("Cap.")
                                            break

                                        elif data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() == data[l][2][i].get_value() and n_way > 0:
                                            data[l][3][i].set_value("H")
                                            data[l][4][i].set_value("")
                                            break

                                        elif n_way <= 0 and (data[l][0][j].get_value() == data[l][0][i].get_value()):   #dobbiamo capire se è miss di cap o di conf
                                            #diff = (i - j - vuoti - (len([x.get_value() for x in data[l][0][j:i]]) - len(set([x.get_value() for x in data[l][0][j:i]]))))
                                            ins = set([x.get_value() for x in data[l][0][j:i] if x.get_value() != ""])
                                            diff  = len(ins)
                                            if (diff <=  cache_table.get_sets()[l] * cache_table.get_ways()[l]):
                                                data[l][4][i].set_value("Conf.")
                                            else:
                                                data[l][4][i].set_value("Cap.")
                                            break
                                            
                                else:
                                    data[l][3][i] = fasi.TipoMiss("H")
                                    data[l][4][i] = fasi.TipoMiss("")
                            
                            else:
                                n_way = cache_table.get_ways()[l]
                                #forse soluzione al problema -> incontri
                                incontri = []

                                for j in range(i-1,-1,-1):
                                    if data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() != data[l][2][i].get_value() and data[l][2][j].get_value() not in incontri:
                                        n_way -= 1
                                        incontri.append(data[l][2][j].get_value())

                                    elif data[l][1][j].get_value() == data[l][1][i].get_value() and data[l][2][j].get_value() == data[l][2][i].get_value() and n_way > 0:
                                        data[l][3][i].set_value("H")
                                        data[l][4][i].set_value("")
                                        break

                                    elif n_way <= 0 and  (data[l][0][j].get_value() == data[l][0][i].get_value()):   #dobbiamo capire se è miss di cap o di conf
                                        #diff = (i - j - vuoti - (len([x.get_value() for x in data[l][0][j:i]]) - len(set([x.get_value() for x in data[l][0][j:i]]))))
                                        ins = set([x.get_value() for x  in data[l][0][j:i] if x.get_value() != ""])
                                        diff  = len(ins)
                                        if (diff <=  cache_table.get_sets()[l] * cache_table.get_ways()[l]):
                                            data[l][4][i].set_value("Conf.")
                                        else:
                                            data[l][4][i].set_value("Cap.")
                                            print(l,f,i)
                                        break
                                
                    #print("Confronto tra " + str(data[l][f][i].get_value()) + " e " + data_utente[l][f][i])
                    #inserire if che controlla se utente ha immesso spazio vuoto + se mi trovo in index e tag e tipo = fully associative -> ok
                    
                    #INSERIRE CONTROLLO CHE SE UTENTE NON HA MESSO NULLA NELLA CELLA -> CONSIDERARE ERRORE E METTERE DATO CORRETTO -> fatto CONTROLLARE
                    #ci sarebbe il problema del vuoto per fully associative e vuoto per "non scrittura" ma caso già preso in considerazione
                    
                    #casistiche = [type(fasi.BlockNumber(1,1)), type(fasi.Index(1,1)), type(fasi.Tag(1,1))]      #?
                    
                    
                    #Per controllare cella per cella, problema perchè quando f == 4, modifico 3
                    #Quindi metto controllo, sia 3 che 4 li controllo quando f == 4

                    #print([[[x.get_value() for x in i] for i in j] for j in data])

                    casistiche = [type(fasi.Tag(1,1))]
                    res3 = None
                    res4 = None
                    if type(data[l][f][i]) in casistiche:
                        res = data[l][f][i].check(data_utente[l][f][i], cache_table.data, l, i)

                        #qui rimodificare valore index
                        if res is not None: 
                            if "invertiti" in res:
                                data[l][1][i].set_value(int(data[l][1][i].get_value().split()[0]))

                    elif f == 3:
                        # non fare nulla
                        continue

                    elif f == 4:
                        res = None
                        res3 = data[l][3][i].check(data_utente[l][3][i])
                        res4 = data[l][f][i].check(data_utente[l][f][i])
                    else: res = data[l][f][i].check(data_utente[l][f][i])

                    #res = data[l][f][i].check(data_utente[l][f][i])
                    if cache_table.get_cache_type()[l] == "fully_associative" and (f == 1 or f == 2):
                        res = None
                        vuoto = data_utente[l][f][i] == ""
                        if not vuoto: res = "Una cache fully associative non utilizza index e tag"
                    #errore perchè M ma non dice quale tipologia di M
                    #CONTROLLARE -> PROBLEMA (SE CHECK COLONNA PER COLONNA PERDO IL CONTROLLO CELLA PER CELLA CHE AVEVO)

                    if res is not None: # there was an error
                        put_error = True
                        if changed_cells is not None and [l,f,i] not in changed_cells: put_error=False 
                        if put_error:
                            errori += 1
                            commenti.append(res)
                            indici_errori.append((l,f,i))
                            #print(type(data[l][f][i]))
                            #print(res, l, f, i)

                    if res3 is not None: # there was an error
                        put_error = True
                        if changed_cells is not None and [l,3,i] not in changed_cells: put_error=False 
                        if put_error:
                            errori += 1
                            commenti.append(res3)
                            indici_errori.append((l,3,i))
                            #print(type(data[l][3][i]))
                            #print(res3, l, 3, i)

                    if res4 is not None: # there was an error
                        put_error = True
                        if changed_cells is not None and [l,4,i] not in changed_cells: put_error=False 
                        if put_error:
                            errori += 1
                            commenti.append(res4)
                            indici_errori.append((l,4,i))
                            #print(type(data[l][4][i]))
                            #print(res, l, 4, i)
                    
                
                """
                for f in range(5+int(cache_table.get_offset())): #aggiunto con alessio

                    casistiche = [type(fasi.Tag(1,1))]
                    if type(data[l][f][i]) in casistiche:
                        res = data[l][f][i].check(data_utente[l][f][i], cache_table.data, l, i)

                        #qui rimodificare valore index
                        if res is not None: 
                            if "invertiti" in res:
                                data[l][1][i].set_value(int(data[l][1][i].get_value().split()[0]))

                    else: res = data[l][f][i].check(data_utente[l][f][i])
                
                    
                    #res = data[l][f][i].check(data_utente[l][f][i])
                    if cache_table.get_cache_type()[l] == "fully_associative" and (f == 1 or f == 2):
                        res = None
                        vuoto = data_utente[l][f][i] == ""
                        if not vuoto: res = "Una cache fully associative non utilizza index e tag"
                    #errore perchè M ma non dice quale tipologia di M
                    #CONTROLLARE -> PROBLEMA (SE CHECK COLONNA PER COLONNA PERDO IL CONTROLLO CELLA PER CELLA CHE AVEVO)
                    
                    #errore se utente mette M anziche H e non fornisce tipologia
                    if f == 4 and data[l][3][i].get_value() == "M" and data[l][f][i].get_value() not in ["L", "Cap.", "Conf."]:
                        res = "Non è stata data una tipologia di Miss"
                    
                    if res is not None: # there was an error
                        put_error = True
                        if changed_cells is not None and [l,f,i] not in changed_cells: put_error=False 
                        if put_error:
                            errori += 1
                            commenti.append(res)
                            indici_errori.append((l,f,i))
                            #print(type(data[l][f][i]))
                            print(res, l, f, i)
                """
                    
            
        #correzione cache finale
        indici_errori_cache_finale = []
        if cache_table.get_lvlinit() != 0:
            cachef = dict()
            init_index_order = list(cache_table.get_init().keys())
            ways = cache_table.get_ways()[cache_table.get_lvlinit()-1]
            for index in init_index_order:
                tags = stor_init[str(index)][-ways:]
                cachef[index] = tags
            #controllo se ci sono elementi presenti nella cache iniziale non "sfruttati"
            for k,v in cache_table.get_init().items():
                if k not in cachef:
                    cachef[k] = v

            cachef = [[str(k)]+v for k,v in cachef.items()]
            cache_table.fin = cachef

            #print(cachef)
            #print(tabf)
            
            for j in range(len(cachef)):
                if str(cachef[j]) != str(tabf[j]):
                    """
                    put_error = True
                    if changed_cells is not None and ["f",j,1] not in changed_cells: put_error=False 
                    if put_error:
                        #indenta il codice sotto v
                    """
                    errori += 1
                    commenti.append("Errore nella cache finale")
                    indici_errori_cache_finale.append(j)
                    #print("Errore nella cache finale   " + str(j))

        return errori, commenti, indici_errori, indici_errori_cache_finale



    