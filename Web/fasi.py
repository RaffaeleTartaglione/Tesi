class Stage():
    value = " "
    errore = "Errore di costruzione"

    def set_value(self, v):
        self.value = v

    def get_value(self):
        return self.value

    def check(self, v):
        if str(self.value) != str(v):
            #controllo se utente ha lasciato cella vuota (non risposta)
            
            # Vedere se specifica casistica:
            # - inversione tra index e tag
            # - quando divisione prendo parte inferiore(?)
            # - inverte dividendo con divisore
            # - inversione di cifre quando trascrive (discalculia)
            if len(str(v))>1 and str(self.value)[::-1] == str(v):
                self.errore = "Attenzione: hai invertito le cifre"
            
            if v != "":
                self.value = v

            return self.errore

class BlockNumber(Stage):
    value = " "
    errore = "Numero di blocco errato"

    def __init__(self, indirizzo, dim_blocco):
        self.value = int(int(indirizzo)/int(dim_blocco))

    def check(self, v):
        if str(self.value) != str(v):
            if len(str(v))>1 and str(self.value)[::-1] == str(v):
                self.errore += ": hai invertito le cifre"
            

            #elif ...

            if v != "":
                if int(v) == int(self.value) + 1:
                    self.errore += ": si deve prendere la parte intera inferiore"
                self.value = v

            return self.errore


class Index(Stage):
    value = " "
    errore = "Index errato"

    def __init__(self, n_blocco, n_set):
        self.value = int(n_blocco) % int(n_set)

    def check(self, v):
        if str(self.value) != str(v):
            if len(str(v))>1 and str(self.value)[::-1] == str(v):
                self.errore += ": hai invertito le cifre"

            #elif ...

            if v != "":
                #devo far sapere al tag che c'è stato un errore nell'index -> separo con segno valore errore con valore correttp
                self.value = str(v)+" "+str(self.value)

            return self.errore


class Tag(Stage):
    value = " "
    errore = "Tag errato"

    def __init__(self, n_blocco, n_set):
        self.value = int(int(n_blocco)/int(n_set))

    def check(self, v, data, l, i):
        if str(self.value) != str(v):
            if len(str(v))>1 and str(self.value)[::-1] == str(v):
                self.errore += ": hai invertito le cifre"
            
            """
            Se si sono invertiti l'indici e il tag:
            - me ne accorgo solo quando correggo il tag (caso inversione) (perchè ancora non mi sono calcolato il tag vista la costruzione dinamica):
                * leggo l'index e c'è un errore -> sostituisco (con il valore del tag MODIFICATO)
                * leggo tag e leggo valore in data di index -> se modificato allora controllo
                * 
            """
            

            #elif ...

            if v != "":
                if " " in str(data[l][1][i].get_value()):
                    utente, giusto = data[l][1][i].get_value().split()
                    if int(v) == int(giusto) and int(self.value) == int(utente):
                        self.errore += ": si sono invertiti l'Index con il Tag"
                if int(v) == int(self.value) + 1:
                    self.errore += ": si deve prendere la parte intera inferiore"
                self.value = v

            return self.errore


class HM(Stage):
    value = " "
    errore = "Hit o Miss errato"

    def __init__(self, hm):
        self.value = hm

class TipoMiss(Stage):
    value = " "
    errore = "Tipo di miss errato"

    def __init__(self, tm):
        self.value = tm


class Offset(Stage):
    value = " "
    errore = "Offset errato"

    def __init__(self, indirizzo, dim_blocco):
        self.value = int(indirizzo) % int(dim_blocco)