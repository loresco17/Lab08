from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        res=[]
        for d in self._distributori:
            prezzo_tot=0
            giorni=0
            media=0
            prezzi=d.get_prezzi()
            for p in prezzi:
                if p.data.month==mese:
                    prezzo_tot+=p.prezzo_litro
                    giorni+=1
            if giorni>0:
                media=prezzo_tot/giorni
            res.append((d.nome, media))
        return res
    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for distributore in self._distributori:
            id_dist=distributore.id
            prezzo_oggi = prezzi_settimana[id_dist][giorno-1]
            costo_carburante = prezzo_oggi * 100
            costo_spostamento = 0
            if ultimo_distributore is not None and ultimo_distributore != id_dist:
                costo_spostamento = 5

            costo_totale_scelta = costo_carburante + costo_spostamento
            sequenza_parziale.append(id_dist)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_dist,
                costo_corrente + costo_totale_scelta,
                prezzi_settimana
            )
            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: Un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        diz={}
        for d in self._distributori:
            prezzi=d.get_prezzi()
            i=0
            sett=[]
            for p in prezzi:
                if i==7:
                    break
                else:
                    if p.data.month==mese:
                        sett.append(p.prezzo_litro)
                        i+=1
            diz[d.id]=sett
        return diz