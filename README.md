# Crycur

&nbsp;&nbsp;&nbsp;&nbsp;
Crycur is a commandline tool that introduces helpful functionalities for blockchain based crypto currency application.
Including, DSA parameter generation, random transaction block generation, proof of work calculation of transaction blocks
for the chain, and validation for transaction blocks as well as the chain itself.   

&nbsp;&nbsp;&nbsp;&nbsp;
Crycur is OS independent. Meaning that, one can start block or dsa parameter generation and/or mining functions in one
operating system and continue in another. Final result will be valid in all operating systems.

**Implemented by:**

 * [M.Mucahid Benlioglu](https://github.com/mbenlioglu)
 * [Mert Kosan](https://github.com/mertkosan)


## Getting Started

**Prerequisites:**

- [Python](https://docs.python.org/2/) (developed and tested in python 2.7)
- [pip](https://pip.pypa.io/en/stable/) for python package management

### Installation and Running

&nbsp;&nbsp;&nbsp;&nbsp;
Firstly, clone or download this repository, then run the following command in the project root to install needed
dependencies
    
    $ pip install -r requirements.txt

After installation succeeds, you can start using the tool by executing the provided functionalities in the following
format

    $ python crycur.py [COMMAND] [OPTIONS]

For more information execute `$ python crycur.py --help`

## Adapted Cryptocurrency Format

&nbsp;&nbsp;&nbsp;&nbsp;
For the proof of work(PoW) algorithm of [mining](https://en.wikipedia.org/wiki/Bitcoin#Mining), sha3_256 is adapted.
Every link of the chain consists of previous link's PoW, Merkle root hash the transaction block, nonce value and PoW of
link.

&nbsp;&nbsp;&nbsp;&nbsp;
Transaction blocks contains number of transactions which are hashed together to form a link in chain. Lastly, DSA parameters
consist of 2 large primes and a generator number.

**Example Transaction:**

    *** Bitcoin transaction ***
    Serial number: 307217148074680400305152224313952843912
    p: 19048168494944007748040397400192319975532006557423228306689086543231957739081924107766832688293691764564143438388412395263055782926823098685975722280398104115250680114205844386021939910971747650259776834788404090407191890847225387752179464018884391149850006988572188284948595588845624071548085823239830412909747077208792607018037728525897345958063942101709068644873743530359687877939644267199232952043255134851061711385840105170041858478516296519691141008312755706469482055609119913841786178247060667837792940073095359627780989622050482703674763731539873811487577313688058097953846602217430512017551343920359732582941
    q: 76620299962535251014217660398861102873449179589067496445746187681031064064779
    g: 5635401192098599368871022780162285493865426560025724532723444671444622857198187081325909237571693542097820004448316297528820177381783243894825425951433448015295136890283968945659036146103716822022523425633979589820238350767854087501041017942256616070427618813054986396600247206954892197456423027913830587554237655800203561898472768378173835169428053540819834685074373008969580941148135383731745252683873628475556095461445665277261675930562061970731323237285418561368551000528028352654060302157706783779540027528124894847196306763794264730955741278349628000388720449951884938269510142001150361674183732212431229633085
    Payer Public Key (beta): 11561463814194164236935604096232260941357135976132825344117384058503325786623955836613017730442267536147853199744445460018024545139345709301912841827286921780284312175566272710229665595887506626582676750369562625069243721710275447149159310228581093647400129197834511374695323153827339320106407939303383286077181257741285435822881449474552464141486898214680129948364113067581713030535413492673659232628949772017037810085775104461583994555862029325631831407817289882512645731879095815358432131189706105819481820741019764273088045110176146012856179403501932353214104676513390078452779341450287842813388398024138108230136
    Payee Public Key (beta): 5399068293198336906816934552409515111673303769767792772666129450005157999385151471823657254811625445714569067040523361389167746825702410292341701890020815920654910426844076017592795698861283602126592600366163821138590428086435110669068596902482188147791490978825888326205734574567282251068502470690851946627973975540527237557434600344960229210507012791990208471665661735139933022942989688422812635666575854488591603820226322824294882757052812458262790173721630628494532285294737194531263690735792382284700220429019830616470094581723246613340369530227458238148342966411455532658744089480167482899206796058316595465047
    Amount: 159 Satoshi
    Signature (r): 15679016414051422551927741732322328985193358337434896684816081627911755878289
    Signature (s): 54263384594195688933119688809194230887830517334781056082567188955628529289592

**Example Link in Chain:**
    
    000000a585da6ab70be4128da8a9583f8888cee1a8a3ff65f05284eea68550d1
    875280714797792d05ea38e57ecfc91dc5406c376f935ec0df45586889f6a41f
    315748198267374607845047734207626022876
    0000000c0d2be69ed5d7c93247de41961999ac2dfa356ef05587842b7f2ff84b

## Acknowledgement
_This project initially created as a part of the term project for **CS411 - Cryptography** lecture of **Sabanci University**_
