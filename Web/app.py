from flask import Flask, render_template, request
from flask.views import View
import cache, genera_indirizzi
import random
import json

app = Flask(__name__)

class ListView(View):
    def get_template_name(self):
        raise NotImplementedError()

    def dispatch_request(self):
        return render_template(self.get_template_name())


class LoginView(ListView):
    def get_template_name(self):
        return 'login.jinja'

app.add_url_rule(
    "/",
    view_func=LoginView.as_view("login-view"),
    methods=["GET", "POST"],
)

#correzione
class MainView(ListView):
    def get_template_name(self):
        return 'main.jinja'
    
app.add_url_rule(
    "/main",
    view_func=MainView.as_view("main-view"),
    methods=["GET", "POST"],
)

#generazione
class GenerateView(ListView):
    def get_template_name(self):
        return 'generazione.jinja'
    
app.add_url_rule(
    "/generazione",
    view_func=GenerateView.as_view("generate-view"),
    methods=["GET", "POST"],
)

#simulazione
class SimulateView(ListView):
    def get_template_name(self):
        return 'simulazione.jinja'
    
app.add_url_rule(
    "/simulazione",
    view_func=SimulateView.as_view("simulate-view"),
    methods=["GET", "POST"],
)

# fully associative -> 1 set e direct mapped -> 1 way

class TableCorrectionView(ListView):
    def get_template_name(self):      
        return 'table.jinja'

    def dispatch_request(self):
        args = request.args
        if request.method == 'POST':
            args = request.form
        params = args.get('params')
        if params is None:
            correction_type = args.get('correction_type')
            clock_number = 0 #clock
            cell_number = 0 #cellnumber
            indirizzi = args.get('indirizzi')
            addresses = [int(i) for i in indirizzi.split()]


            cache_type = [args.get('cache_type')]
            data_type = args.get('data_type')
            info_data_type = [args.get('data_type')]
            if data_type == "byte":
                data_type = [1]
            elif data_type == "half word":
                data_type = [2]
            else:   #word
                data_type = [4]
            lvl = int(args.get('lvl',1))
            offset = args.get('offset') == "yes"

            data_dim = [int(args.get("dato"))]
            sets = [int(args.get('set'))]
            ways = [int(args.get('n-way'))]

            cache_type2 = args.get('cache_type2')
            data_type2 = args.get('data_type2')
            info_data_type2 = args.get('data_type2')
            if data_type2 == "byte":
                data_type2 = 1
            elif data_type2 == "half word":
                data_type2 = 2
            else:   #word
                data_type2 = 4
            data_dim2 = int(args.get("dato2") or 0)
            sets2 = int(args.get('set2') or 0)
            ways2 = int(args.get('n-way2') or 0)
            
            cache_type.append(cache_type2)
            data_type.append(data_type2)
            data_dim.append(data_dim2)
            sets.append(sets2)
            ways.append(ways2)

            info_data_type.append(info_data_type2)
            info_cache = [cache_type, data_dim, info_data_type, sets, ways]

            init = args.getlist("cell_value_i")
            lvlinit = int(args.get('lvlinit'))
            if args.get('initial') != "yes":
                lvlinit = 0

            cacheinit = dict()
            linit = []
            if init != []:
                for i in range(0,len(init),ways[lvlinit-1]+1):
                    cacheinit[int(init[i])] = init[i+1:i+ways[lvlinit-1]+1]     
                    linit.append(init[i:i+ways[lvlinit-1]+1])                  

        else:
            print("sto qua")
            addresses, cache_type, data_type, data_dim, sets, ways, lvl, offset, init, lvlinit, clock_number, cell_number, cacheinit, linit, info_data_type, info_cache, correction_type = json.loads(args.get('params'))
            clock_number += 1
            cell_number += 1

        self.correction_type = correction_type

        params = json.dumps([addresses, cache_type, data_type, data_dim, sets, ways, lvl, offset, init, lvlinit, clock_number, cell_number, cacheinit, linit, info_data_type, info_cache, correction_type])
        
        level_number = cell_number//((5+int(offset))*len(addresses))
        
        global cache_table
        cache_table = cache.Cache(addresses, cache_type, data_type, data_dim, sets, ways, lvl, offset, cacheinit, lvlinit)

        addresses.insert(0, "Address")
        tables = []
        for idx in range(lvl):
            if correction_type == 'esame' or f'cell_value_{idx+1}' not in args:
                empty = [["" for i in addresses[1:]] for i in range(5+int(cache_table.get_offset()))]
            else:
                empty = args.getlist(f'cell_value_{idx+1}')
                lunghezza = len(addresses)
                empty = [empty[i+1: i + lunghezza] for i in range(0, len(empty), lunghezza)]

            empty[0].insert(0, "Block#")
            empty[1].insert(0, "Index")
            empty[2].insert(0, "Tag")
            empty[3].insert(0, "Hit/Miss")
            empty[4].insert(0, "Tipo miss")
            if offset:
                empty[5].insert(0, "Offset")

            tables.append((idx+1,addresses, empty))

        tmp = args.getlist(f'cell_value_f')
        cachef = []
        i = 0
        for r in range(sets[lvlinit-1]):
            row = []
            for c in range(ways[lvlinit-1]+1):
                if len(tmp)> 0 and correction_type != "esame": row.append(tmp[i])
                else: row.append('')
                i+=1
            cachef.append(row)

        return render_template(self.get_template_name(), tables=tables, init=linit, cachef=cachef, lvlinit=lvlinit, info_cache=info_cache, lvl=lvl, params=params)

app.add_url_rule(
    "/cachec",
    view_func=TableCorrectionView.as_view("tablec-view"),
    methods=["GET", "POST"],
)

class TableGenerateView(ListView):
    def get_template_name(self):
        return 'tableg.jinja'

    def dispatch_request(self):
        args = request.args
        if request.method == 'POST':
            args = request.form

        n_indirizzi = int(args.get('naddresses'))
        size_max = int(args.get('size_max'))
        tipo_miss = args.get('tipo_miss')
        lvlrif = int(args.get('lvlrif'))                                       

        cache_type = [args.get('cache_type')]
        data_type = args.get('data_type')
        info_data_type = [args.get('data_type')]
        if data_type == "byte":
            data_type = [1]
        elif data_type == "half word":
            data_type = [2]
        else:   #word
            data_type = [4]
        data_dim = [int(args.get("dato"))]
        lvl = int(args.get('lvl',1))
        offset = args.get('offset') == "yes"

        sets = [int(args.get('set'))]
        ways = [int(args.get('n-way'))]
        
        cache_type2 = args.get('cache_type2')
        data_type2 = args.get('data_type2')
        info_data_type2 = args.get('data_type2')
        if data_type2 == "byte":
            data_type2 = 1
        elif data_type2 == "half word":
            data_type2 = 2
        else:   #word
            data_type2 = 4
        data_dim2 = int(args.get("dato2") or 0)
        sets2 = int(args.get('set2') or 0)
        ways2 = int(args.get('n-way2') or 0)

        cache_type.append(cache_type2)
        data_type.append(data_type2)
        data_dim.append(data_dim2)
        sets.append(sets2)
        ways.append(ways2)

        info_data_type.append(info_data_type2)
        
        info_cache = [cache_type, data_dim, info_data_type, sets, ways]

        init = args.getlist("cell_value_i")
        lvlinit = int(args.get('lvlinit'))
        if args.get('initial') != "yes":
            lvlinit = 0

        cacheinit = dict()
        linit = []
        if init != []:
            #ways+1 (index+tags) al posto di 2
            for i in range(0,len(init),ways[lvlinit-1]+1):
                cacheinit[int(init[i])] = init[i+1:i+ways[lvlinit-1]+1] 
                linit.append(init[i:i+ways[lvlinit-1]+1])                  

        if lvlrif == 1:
            addresses, distanza, ind1, ind2 = genera_indirizzi.genera_indirizzi(tipo_miss, size_max, data_type[0]*data_dim[0], sets[0], ways[0], n_indirizzi)

        elif lvlrif == 2: #devo testare random_addresses perchè dipende dai vuoti             
            #creo l'oggetto cache con input dati
            #lo passo con solo un livello alla funzione riempicache()
            #conto quante Hit sono state trovate e mi salvo i loro indici -> saranno i vuoti nel secondo livello
            #i vuoti incideranno sui calcoli per la distanza degli indici -> se i vuoti si trovano tra loro

            ricalcolo = True
            while ricalcolo:
                #calcola dim blocco 
                addresses, distanza, ind1, ind2 = genera_indirizzi.genera_indirizzi(tipo_miss, size_max, data_type[1]*data_dim[1], sets[1], ways[1], n_indirizzi)
                indici = []
                candidate = cache.Cache(addresses, cache_type, data_type, data_dim, sets, ways, 1, offset, cacheinit, lvlinit)                        #livello impostato a 1
                candidate.riempicache()
                dati = candidate.data[0]
                #anzichè range, dovrei vedere se ci sono hit tra i due indici
                for i in range(ind1+1, ind2):
                    if dati[3][i].get_value() == "H":
                        indici.append(i)
                
                #se vuoti non incidono:
                #hit sopra -> colonne vuote sotto -> distanza diminuisce
                nuova_distanza = distanza - len(indici)
                #se distanza va comunque bene
                if (tipo_miss == "cap" and nuova_distanza > sets[1]*ways[1]) or (tipo_miss == "conf"): #and nuova_distanza <= sw):
                    ricalcolo = False
        
        else:
            addresses = []
            #semplicemente genera lista indirizzi randomicamente
            for x in range(n_indirizzi):
                addresses.append(random.randint(1,size_max))

        global cache_table
        cache_table = cache.Cache(addresses, cache_type, data_type, data_dim, sets, ways, lvl, offset, cacheinit, lvlinit)
        cache_table.riempicache()
        dati = cache_table.data
        dati = [[[x.get_value() for x in i] for i in j] for j in dati]

        for l in range(len(dati)):
            dati[l][0].insert(0, "Block#")
            dati[l][1].insert(0, "Index")
            dati[l][2].insert(0, "Tag")
            dati[l][3].insert(0, "Hit/Miss")
            dati[l][4].insert(0, "Tipo miss")
            if offset:
                dati[l][5].insert(0, "Offset")

        addresses.insert(0, "Address")

        #if lvlinit != 0:
        #prendo la cache finale
        #passare cache finale in render_template
        #modificare value della tabella della cache finale
        cachefin = []
        if lvlinit != 0:
            cachefin = cache_table.fin

        tables = []
        for i in range(lvl):
            tables.append((i+1,addresses, dati))
        return render_template(self.get_template_name(), tables=tables, init=linit, lvlinit=lvlinit, cachefin=cachefin, cache_type=cache_type, n_indirizzi=len(addresses), info_cache=info_cache, lvl=lvl)

app.add_url_rule(
    "/cacheg",
    view_func=TableGenerateView.as_view("tableg-view"),
    methods=["GET", "POST"],
)

class TableSimulateView(ListView):
    def get_template_name(self):
        return 'tables.jinja'

    def dispatch_request(self):
        args = request.args
        if request.method == 'POST':
            args = request.form

        if not args.get('params'):
            clock_number = 0 #clock
            cell_number = 0 #cellnumber
            n_indirizzi = int(args.get('naddresses'))
            size_max = int(args.get('size_max'))
            tipo_miss = args.get('tipo_miss')
            lvlrif = int(args.get('lvlrif'))

            cache_type = [args.get('cache_type')]
            data_type = args.get('data_type')
            info_data_type = [args.get('data_type')]
            if data_type == "byte":
                data_type = [1]
            elif data_type == "half word":
                data_type = [2]
            else:   #word
                data_type = [4]
            data_dim = [int(args.get("dato"))]
            lvl = int(args.get('lvl',1))
            offset = args.get('offset') == "yes"

            sets = [int(args.get('set'))]
            ways = [int(args.get('n-way'))]
            
            cache_type2 = args.get('cache_type2')
            data_type2 = args.get('data_type2')
            info_data_type2 = args.get('data_type2')
            if data_type2 == "byte":
                data_type2 = 1
            elif data_type2 == "half word":
                data_type2 = 2
            else:   #word
                data_type2 = 4
            data_dim2 = int(args.get("dato2") or 0)
            sets2 = int(args.get('set2') or 0)
            ways2 = int(args.get('n-way2') or 0)

            cache_type.append(cache_type2)
            data_type.append(data_type2)
            data_dim.append(data_dim2)
            sets.append(sets2)
            ways.append(ways2)

            info_data_type.append(info_data_type2)
            
            init = args.getlist("cell_value_i")
            lvlinit = int(args.get('lvlinit'))

            cacheinit = dict()
            linit = []
            if init != [] and lvlinit == 1:
                for i in range(0,len(init),ways[lvlinit-1]+1):
                    cacheinit[int(init[i])] = init[i+1:i+ways[lvlinit-1]+1]     
                    linit.append(init[i:i+ways[lvlinit-1]+1])                   

            else:
                for n in range(sets[0]):
                    cacheinit[n] = [""]*ways[0]
                    l = [n]
                    for x in range(ways[0]):
                        l.append("")
                    linit.append(l)
            
            #[index, LRU, (V, tag)*ways]

            for i in range(len(linit)):
                if "" not in linit[i]:
                    lru = 0
                else:
                    lru = linit[i].index("")-1
                linit[i].insert(1,lru)

            for j in range(len(linit)):
                temp = []
                for x in range(len(linit[j])):
                    if x > 1:
                        temp.append("")     #bit
                    temp.append(linit[j][x])
                linit[j] = temp

            print("LINIT")
            print(linit)

            if args.get('initial') != "yes":
                lvlinit = 0

            if lvlrif == 1:
                addresses, distanza, ind1, ind2 = genera_indirizzi.genera_indirizzi(tipo_miss, size_max, data_type[0]*data_dim[0], sets[0], ways[0], n_indirizzi)

            elif lvlrif == 2: #devo testare random_addresses perchè dipende dai vuoti
                #creo l'oggetto cache con input dati
                #lo passo con solo un livello alla funzione riempicache()
                #conto quante Hit sono state trovate e mi salvo i loro indici -> saranno i vuoti nel secondo livello
                #i vuoti incideranno sui calcoli per la distanza degli indici -> se i vuoti si trovano tra loro

                ricalcolo = True
                while ricalcolo:
                    #calcola dim blocco 
                    addresses, distanza, ind1, ind2 = genera_indirizzi.genera_indirizzi(tipo_miss, size_max, data_type[1]*data_dim[1], sets[1], ways[1], n_indirizzi)
                    indici = []
                    candidate = cache.Cache(addresses, cache_type, data_type, data_dim, sets, ways, 1, offset, cacheinit, lvlinit)                        #livello impostato a 1
                    candidate.riempicache()
                    dati = candidate.data[0]
                    #anzichè range, dovrei vedere se ci sono hit tra i due indici
                    for i in range(ind1+1, ind2):
                        if dati[3][i].get_value() == "H":
                            indici.append(i)
                    
                    #se vuoti non incidono:
                    #hit sopra -> colonne vuote sotto -> distanza diminuisce
                    nuova_distanza = distanza - len(indici)
                    #se distanza va comunque bene
                    if (tipo_miss == "cap" and nuova_distanza > sets[1]*ways[1]) or (tipo_miss == "conf"): #and nuova_distanza <= sw):
                        ricalcolo = False
            
            else:
                addresses = []
                #semplicemente genera lista indirizzi randomicamente
                for x in range(n_indirizzi):
                    addresses.append(random.randint(1,size_max))
        
        else:
            addresses, n_indirizzi, size_max, tipo_miss, lvlrif, cache_type, data_type, data_dim, sets, ways, lvl, offset, init, lvlinit, clock_number, cell_number, cacheinit, linit, info_data_type = json.loads(args.get('params'))
            clock_number += 1
            cell_number += 1

        level_number = cell_number//(5*n_indirizzi)

        if level_number == 1 and (cell_number-1)//(5*n_indirizzi) == 0:
            cacheinit = dict()
            linit = []
            if init != [] and lvlinit == 2:
                for i in range(0,len(init),ways[lvlinit-1]+1):
                    cacheinit[int(init[i])] = init[i+1:i+ways[lvlinit-1]+1]     
                    linit.append(init[i:i+ways[lvlinit-1]+1])                   

            else:
                for n in range(sets[1]):
                    cacheinit[n] = [""]*ways[1]
                    l = [n]
                    for x in range(ways[1]):
                        l.append("")
                    linit.append(l)
            
            #[index, LRU, (V, tag)X#vie]
            #quando calcolo lru, devo controllare se "" not in linit[i] escludendo le posizioni in cui c'è il bit di validità

            for i in range(len(linit)):
                if "" not in linit[i]:
                    lru = 0
                else:
                    lru = linit[i].index("")-1
                linit[i].insert(1,lru)

            for j in range(len(linit)):
                temp = []
                for x in range(len(linit[j])):
                    if x > 1:
                        temp.append("")     #bit
                    temp.append(linit[j][x])
                linit[j] = temp

        info_cache = [cache_type, data_dim, info_data_type, sets, ways]

        global cache_table
        cache_table = cache.Cache(addresses, cache_type, data_type, data_dim, sets, ways, lvl, offset, cacheinit, lvlinit)
        cache_table.riempicache()
        dati = cache_table.data
        dati = [[[x.get_value() for x in i] for i in j] for j in dati]
        
        row_cella_cambiata = -1
        col_cella_cambiata = -1
        if cell_number%5 == 3:
            col = (cell_number//5)%(n_indirizzi)+1
            index_dati = dati[level_number][1][col-1] #forse - 2
            tag_dati = dati[level_number][2][col-1]
            for i in range(len(linit)):
                if linit[i][0] == index_dati:
                    lru = linit[i][1]*2+3
                    tags = linit[i][3::2] 
                    #se non troviamo riscontri
                    if tag_dati not in tags:
                        print("Tag non presente nella cache, quindi abbiamo una Miss")
                        linit[i][lru] = tag_dati   #aggiorno tag nella cella indicata dal LRU
                        linit[i][lru-1] = 1        #aggiorno il bit di validità
                        if linit[i][1] < ways[level_number] - 1: #aggiorno LRU
                            linit[i][1] += 1
                        else: linit[i][1] = 0
                        row_cella_cambiata = i
                        col_cella_cambiata = lru
        else:
            tmp = cell_number
            while tmp%5 != 3:
                tmp -= 1
            if tmp >= 0:
                col = (tmp//5)%(n_indirizzi)+1
                index_dati = dati[level_number][1][col-1]
                tag_dati = dati[level_number][2][col-1]
                for i in range(len(linit)):
                    if linit[i][0] == index_dati:
                        lru = linit[i][1]*2+3
                        tags = linit[i][3::2] 
                        #se non troviamo riscontri
                        if tag_dati not in tags:
                            linit[i][lru] = tag_dati   #aggiorno tag nella cella indicata dal LRU
                            linit[i][lru-1] = 1        #aggiorno il bit di validità
                            if linit[i][1] < ways[level_number] - 1: #aggiorno LRU
                                linit[i][1] += 1       #FORSE REGOLA DIVERSA
                            else: linit[i][1] = 0
            else:
                pass # reinizializza se vuoi linit

        params = json.dumps([addresses, n_indirizzi, size_max, tipo_miss, lvlrif, cache_type, data_type, data_dim, sets, ways, lvl, offset, init, lvlinit, clock_number, cell_number, cacheinit, linit, info_data_type])

        for l in range(len(dati)):
            dati[l][0].insert(0, "Block#")
            dati[l][1].insert(0, "Index")
            dati[l][2].insert(0, "Tag")
            dati[l][3].insert(0, "Hit/Miss")
            dati[l][4].insert(0, "Tipo miss")
            if offset:
                dati[l][5].insert(0, "Offset")

        """
        dobbiamo tenere conto delle eventiali colonne vuote
        sebbene sappiamo il livello in cui potrebbe apparire cap o conf, non se abbiamo la certezza
        SOLUZIONE: - preventivamente creare due cache di tipo fully associative, una per il lvl1 e una per il lvl2
                   - passare alla pagina web la lista che conprende i dati delle due cache (l=[fully_associative1, fully_associative2])
                   - nella pagina web in base al livello a cui ci troviamo mostreremo o l'una o l'altra
        """
        col_tab_miss = (cell_number//5)%(n_indirizzi)+1
        # far comparire tab_miss fino alla colonna a cui mi trovo
        # non far comparire la seconda e terza riga

        fully_associative = cache.Cache(addresses, ["fully_associative",""], data_type, data_dim, sets, ways, 1, offset, cacheinit, 0)
        fully_associative.riempicache()
        tab_miss = fully_associative.data
        tab_miss = [[[tab_miss[j][i][x].get_value() if i not in [1,2] else "" for x in range(len(tab_miss[j][i])) if x<col_tab_miss-1] for i in range(len(tab_miss[j]))] for j in range(len(tab_miss))]

        for l in range(len(tab_miss)):
            tab_miss[l][0].insert(0, "Block#")
            tab_miss[l][1].insert(0, "")
            tab_miss[l][2].insert(0, "")
            tab_miss[l][3].insert(0, "Hit/Miss")
            tab_miss[l][4].insert(0, "Tipo miss")
            if offset:
                tab_miss[l][5].insert(0, "Offset")

        tab_miss2 = [0]

        if lvl == 2:
            fully_associative2 = cache.Cache(addresses, [data_type[0],"fully_associative"], data_type, data_dim, sets, ways, 2, offset, cacheinit, 0)
            fully_associative2.riempicache()
            tab_miss2 = fully_associative2.data
            tab_miss2 = [[[tab_miss2[j][i][x].get_value() if i not in [1,2] else "" for x in range(len(tab_miss2[j][i])) if x<col_tab_miss-1] for i in range(len(tab_miss2[j]))] for j in range(len(tab_miss2))]

            for l in range(len(tab_miss2)):
                tab_miss2[l][0].insert(0, "Block#")
                tab_miss2[l][1].insert(0, "")
                tab_miss2[l][2].insert(0, "")
                tab_miss2[l][3].insert(0, "Hit/Miss")
                tab_miss2[l][4].insert(0, "Tipo miss")
                if offset:
                    tab_miss2[l][5].insert(0, "Offset")

        addresses.insert(0, "Address")

        tables = []
        for i in range(lvl):
            tables.append((i+1,addresses, dati))

        tab_miss = [tab_miss[0],tab_miss2[0]]

        return render_template(self.get_template_name(), tables=tables, init=linit, lvlinit=lvlinit, params=params, clock_number=clock_number, cell_number=cell_number, level_number=level_number, 
        n_indirizzi=n_indirizzi, ways=ways, tab_miss=tab_miss, cache_type=cache_type, info_cache=info_cache, lvl=lvl, row_cella_cambiata=row_cella_cambiata, col_cella_cambiata=col_cella_cambiata, offset=offset)

app.add_url_rule(
    "/caches",
    view_func=TableSimulateView.as_view("tables-view"),
    methods=["GET", "POST"],
)

class CheckView(ListView):
    def get_template_name(self):
        return 'check.jinja'

    def dispatch_request(self):
        tab1 = request.form.getlist("cell_value_1")
        utab1 = request.form.getlist("cell_value_1")
        params = request.form.get('params')
        correction_type = json.loads(params)[-1]
        changed_cells = None
        if correction_type == "cella":
            changed_cells = json.loads(request.form.get('changed_cells'))
        tab2 = request.form.getlist("cell_value_2")     #vuoto se lvl = 1
        utab2 = request.form.getlist("cell_value_2")

        list_tabi = request.form.getlist("cell_value_i")     #cache iniziale
        list_tabf = request.form.getlist("cell_value_f")     #cache finale
        tabi = []
        tabf = []
        if len(list_tabi) > 0:
            w = cache_table.get_ways()[cache_table.get_lvlinit()-1]
            for i in range(0,len(list_tabf),w+1):
                tabi.append(list_tabi[i:i+w+1])
                tabf.append(list_tabf[i:i+w+1])

        lunghezza = len(cache_table.get_addresses())

        tab1 = [[tab1[i + 1:i + lunghezza] for i in range(0, len(tab1), lunghezza)]]
        utab1 = [[utab1[i:i + lunghezza] for i in range(0, len(utab1), lunghezza)]]
        tab2 = [[tab2[i + 1:i + lunghezza] for i in range(0, len(tab2), lunghezza)]]
        utab2 = [[utab2[i:i + lunghezza] for i in range(0, len(utab2), lunghezza)]]
        #slicing per eliminare scritte
        data_utente = tab1 + tab2
        utab = utab1 + utab2

        errori, commenti, indici_errori, indici_errori_cache_finale = cache_table.correggi(data_utente,tabf,changed_cells)
        
        rag_commenti = dict()
        for item in commenti:
            if item not in rag_commenti:
                rag_commenti[item] = 1
            else:
                rag_commenti[item] += 1

        addresses = cache_table.get_addresses()

        tables = []
        for i in range(cache_table.get_lvl()):
            tables.append((i+1,addresses, utab))

        errori_commento_pos = []
        indici_totali = indici_errori + indici_errori_cache_finale
        for i in range(len(indici_totali)):
            errori_commento_pos.append((commenti[i], indici_totali[i]))
        
        
        return render_template(self.get_template_name(), tables=tables, errori=errori, rag_commenti=rag_commenti, init=tabi, tabf=tabf, lvlrif=cache_table.get_lvlinit(), ie=indici_errori, iecf=indici_errori_cache_finale, ecp=errori_commento_pos, params=params)

app.add_url_rule(
    "/check",
    view_func=CheckView.as_view("check-view"),
    methods=["GET", "POST"],
)

app.run(debug=True)