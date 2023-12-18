# Marketplace
Implementare:

Producatorii au fiecare un id, care incepe de la 0. Fiecarui producator, ii corespunde
deasemenea o dimensiune a listei de produse necesara pentru a determina cand se
ajunge la limita maxima. Cand un producator se inregistreaza, i se incrementeaza
id-ul si se adauga in lista de size-uri dimesiunea initial 0. Pentru adaugarea
unui producator am facut sincronizarea cu lock-ul prod-lock.

Cand un producator publica un produs, daca limita de publicari nu este depasita,
se incrementeaza size-ul listei de produse, se adauga produsul in lista de
produse a magazinului si se adauga o intrare in dictionarul product_producers,
necesar in functia remove_from_cart.

Un nou cart adaugat presupune incrementarea sincronizata a id_cons si, in dictionarul
de cosuri, inserarea unei intrari cu cheia id-ul si o lista initial goala pentru
valoare unde vor fi introduse produsele.

Pentru adaugarea in cos, se verifica intai ca produsul sa existe, apoi se
sterge din lista de produse a magazinului.

Un lock pentru sincronizare a fost folosit si pentru actiunea de eliminare din cos,
caz in care intervine rolul dictionarului cu legatura produs-producator. Produsul
scos din cos este adaugat inapoi in lista de produse, iar dimensiunea listei de
produse a producatorului e incrementata.

Pentru afisarea cosului final, in consumer, am facut si o sincronizare a printarii,
deoarece fara sincronizare testul 10 nu trecea.

Organizare:
Am folosit modulul logger pentru generarea fisierelor log. Mesajele de log au fost
adaugate la inceputul fiecarei functii, deoarece pentru adaugarea inainte de
return se intampla o desincronizare.
