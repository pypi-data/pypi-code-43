from datetime import datetime
from random import randint
from numpy import random

__all__ = ['Randomize', 'random_text_unicode', 'random_text', 'random_float',
           'random_datetime', 'random_list_element', 'random_bool']

VAL_UNICOD = """'\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f\x10
\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d
\x1e\x1f!"#$%&\'()*+,-./0123456789:;<=>?
040@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`a
bcdefghijklmnopqrstuvwxyz{|}~\x7f 0080€\x81‚ƒ„…†‡ˆ‰Š‹Œ
\x8dŽ\x8f\x90‘’“”•–—˜™š›œ\x9džŸ 00A0 ¡¢£¤¥¦§¨©ª«¬\xad®¯
°±²³´µ¶·¸¹º»¼½¾¿ 00C0ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß
00E0àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ 0100ĀāĂăĄąĆćĈĉĊċČčĎďĐ
đĒēĔĕĖėĘęĚěĜĝĞğ 0120ĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿ 01
40ŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞş 0160ŠšŢţŤťŦŧŨũŪūŬŭŮůŰű
ŲųŴŵŶŷŸŹźŻżŽžſ 0180ƀƁƂƃƄƅƆƇƈƉƊƋƌƍƎƏƐƑƒƓƔƕƖƗƘƙƚƛƜƝƞƟ 01A
0ƠơƢƣƤƥƦƧƨƩƪƫƬƭƮƯưƱƲƳƴƵƶƷƸƹƺƻƼƽƾƿ 01C0ǀǁǂǃǄǅǆǇǈǉǊǋ
ǌǍǎǏǐǑǒǓǔǕǖǗǘǙǚǛǜǝǞǟ 01E0ǠǡǢǣǤǥǦǧǨǩǪǫǬǭǮǯǰǱǲǳǴǵǶǷǸǹ
ǺǻǼǽǾǿ 0200ȀȁȂȃȄȅȆȇȈȉȊȋȌȍȎȏȐȑȒȓȔȕȖȗȘșȚțȜȝȞȟ 0220ȠȡȢȣȤȥ
ȦȧȨȩȪȫȬȭȮȯȰȱȲȳȴȵȶȷȸȹȺȻȼȽȾȿ 0240ɀɁɂɃɄɅɆɇɈɉɊɋɌɍɎɏɐɑɒɓɔɕɖɗɘə
ɚɛɜɝɞɟ 0260ɠɡɢɣɤɥɦɧɨɩɪɫɬɭɮɯɰɱɲɳɴɵɶɷɸɹɺɻɼɽɾɿ 0280ʀʁʂʃʄʅ
ʆʇʈʉʊʋʌʍʎʏʐʑʒʓʔʕʖʗʘʙʚʛʜʝʞʟ 02A0ʠʡʢʣʤʥʦʧʨʩʪʫʬʭʮʯʰʱʲʳʴ
ʵʶʷʸʹʺʻʼʽʾʿ 02C0ˀˁ˂˃˄˅ˆˇˈˉˊˋˌˍˎˏːˑ˒˓˔˕˖˗˘˙˚˛˜˝˞˟ 02E0ˠˡˢ
ˣˤ˥˦˧˨˩˪˫ˬ˭ˮ˯˰˱˲˳˴˵˶˷˸˹˺˻˼˽˾˿ ̛̖̗̘̙̜̝̞̟̀́̂̃̄̅̆̇̈̉̊̋̌̍̎̏̐̑̒̓̔̕̚ ̴̵̶̷̸̡̢̧̨̠̣̤̥̦̩̪̫̬̭̮̯̰̱̲̳
̹̺̻̼̽̾̿ 0͇͈͉͍͎̀́͂̓̈́͆͊͋͌ͅ͏͓͔͕͖͙͚͐͑͒͗͛͘͜͟͝͞ 0360ͣͤͥͦͧͨͩͪͫͬͭͮͯ͢͠͡ͰͱͲͳʹ͵Ͷͷ\u0378\u0379ͺͻͼͽ;Ϳ 
\u0380\u0381\u0382\u0383΄΅Ά·ΈΉΊ\u038bΌ\u038dΎΏΐΑΒΓΔΕΖΗΘΙ
ΚΛΜΝΞΟGreek03A0ΠΡ\u03a2ΣΤΥΦΧΨΩΪΫάέήίΰαβγδεζηθικλμνξο 03
C0πρςστυφχψωϊϋόύώϏϐϑϒϓϔϕϖϗϘϙϚϛϜϝϞϟ 03E0ϠϡϢϣϤϥϦϧϨϩϪϫ
ϬϭϮϯϰϱϲϳϴϵ϶ϷϸϹϺϻϼϽϾϿ0400ЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОП
Cyrillic0420РСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмноп 0440рстуфхцч
шщъыьэюяѐёђѓєѕіїјљњћќѝўџ 0460ѠѡѢѣѤѥѦѧѨѩѪѫѬѭѮѯѰ
ѱѲѳѴѵѶѷѸѹѺѻѼѽѾѿ 0480Ҁҁ҂҃҄҅҆҇҈҉ҊҋҌҍҎҏҐґҒғҔҕҖҗҘҙҚқҜҝ
Ҟҟ 04A0ҠҡҢңҤҥҦҧҨҩҪҫҬҭҮүҰұҲҳҴҵҶҷҸҹҺһҼҽҾҿ 04C0ӀӁӂӃӄ
ӅӆӇӈӉӊӋӌӍӎӏӐӑӒӓӔӕӖӗӘәӚӛӜӝӞӟ 04E0ӠӡӢӣӤӥӦӧӨөӪӫӬӭӮӯӰӱӲӳӴ
ӵӶӷӸӹӺӻӼӽӾӿ 0500ԀԁԂԃԄԅԆԇԈԉԊԋԌԍԎԏԐԑԒԓԔԕԖԗԘ
ԙԚԛԜԝԞԟKomi0520ԠԡԢԣԤԥԦԧԨԩԪԫԬԭԮԯ\u0530ԱԲԳԴԵԶԷԸԹԺԻԼ
ԽԾԿArmenian0540ՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔՕՖ\u0557\u0558ՙ՚՛՜՝
՞՟ ՠաբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտ 0580րցւփքօֆևֈ։֊
\u058b\u058c֍֎֏\u0590֑֖֛֚֒֓֔֕֗֘֙֜֝֞֟Hebrew05A0ְֱֲֳִֵֶַָֹֺֻּֽ֢֣֤֥֦֧֪֭֮֠֡֨֩֫֬֯־ֿ 05C0׀ׁׂ׃ׅׄ׆ׇ\u05c8\u05c9\u05ca
\u05cb\u05cc\u05cd\u05ce\u05cfאבגדהוזחטיךכלםמן 05E0נסעףפץצ
קרשת\u05eb\u05ec\u05ed\u05eeׯװױײ׳
״\u05f5\u05f6\u05f7\u05f8\u05f9\u05fa\u05fb\u05fc\u05fd\u05fe\u05ffYi
ddish0600\u0600\u0601\u0602\u0603\u0604\u0605؆؇؈
؉؊؋،؍؎؏ؘؙؚؐؑؒؓؔؕؖؗ؛\u061c\u061d؞؟Arabic0620ؠءآأؤإئابةتثجحخدذرزسشصضطظعغػؼؽ
ؾؿ ـفقكلمنهوىيًٌٍَُِّْٕٖٜٟٓٔٗ٘ٙٚٛٝٞ 0660٠١٢٣٤٥٦٧٨٩٪٫٬٭ٮٯٰٱٲٳٴٵٶٷٸٹٺٻټٽپٿ 0680ڀځڂڃڄ
څچڇڈډڊڋڌڍڎڏڐڑڒړڔڕږڗژڙښڛڜڝڞڟ 06A0ڠڡڢڣڤڥڦڧڨکڪګڬڭڮگڰڱڲڳڴڵڶڷڸ
ڹںڻڼڽھڿ 06C0ۀہۂۃۄۅۆۇۈۉۊۋیۍێۏېۑےۓ۔ەۖۗۘۙۚۛۜ\u06dd۞۟ 06E0ۣ۠ۡۢۤۥۦۧۨ۩۪ۭ۫۬ۮۯ۰۱۲۳۴۵۶۷۸۹ۺۻۼ۽۾ۿ
 ܀܁܂܃܄܅܆܇܈܉܊܋܌܍\u070e\u070fܐܑܒܓܔܕܖܗܘܙܚܛܜܝܞܟSyriac0720ܠܡܢܣܤܥܦܧܨ
ܩܪܫܬܭܮܯܱܴܷܸܹܻܼܾܰܲܳܵܶܺܽܿ 0740݂݄݆݈݀݁݃݅݇݉݊\u074b\u074cݍݎݏݐݑݒݓݔݕݖݗݘݙݚݛݜݝݞݟ 0760ݠݡݢݣݤݥ
ݦݧݨݩݪݫݬݭݮݯݰݱݲݳݴݵݶݷݸݹݺݻݼݽݾݿ 0780ހށނރބޅކއވމފދތލގޏސޑޒޓޔޕޖޗޘޙޚޛޜޝޞޟ
Thaana07A0ޠޡޢޣޤޥަާިީުޫެޭޮޯްޱ\u07b2\u07b3\u07b4\u07b5\u07b6\u07b7\u07b8
\u07b9\u07ba\u07bb\u07bc\u07bd\u07be\u07bf 07C0߀߁߂߃߄߅߆߇߈߉ߊߋߌߍߎߏ
ߐߑߒߓߔߕߖߗߘߙߚߛߜߝߞߟ 07E0ߠߡߢߣߤߥߦߧߨߩߪ߲߫߬߭߮߯߰߱߳ߴߵ߶߷߸߹ߺ\u07fb\u07fc߽߾߿'
""".replace('\n', '')
VAL_UNICOD += '\n'
VAL_UNICODE_LEN = len(VAL_UNICOD) - 1

VAL = """ЗоV2КСЕYщТъвелJ-РшIlьжтa5BH6Zt
ПЮО1GрTScаghxкvzUNЦгЖУФ0qАdпЭ бoяfyНуi
jШиAm3wWЪДCɑнИЧnbsЙEГ9фkюFXЁЫDыйцeхR4-М
ХдpзЩuKO7ЛЯPMБ8счмёВLЬQr            """.replace('\n', '')

VAL_LEN = len(VAL) - 1


class Randomize(list):

    def element(self):
        """:return random element of self"""
        return self[randint(0, len(self) - 1)]

    def elements(self, count: int):
        """:return list of random elements of self"""
        return [self.element() for _ in range(count)]

    def group_elements(self, count: int):
        """:return concat string of random elements list
            >>> s = Randomize([1,2,4,5])
            >>>example: s.group_elements(2)
            <<< '1 5'
        """
        elem = self.elements(count)
        return self._group(elem)

    @staticmethod
    def _group(iterable):
        return ' '.join([str(s) for s in iterable])

    def pop(self, index: int = None):
        """
        pop del rundom element and return him.
        if pass index number, pop will be used as list.pop
        :param index:
        :return:
        """
        if None:
            return super().pop(randint(0, len(self)))
        else:
            return super().pop(-1)


def random_text_unicode(size: int = 1, random_size=False) -> str:
    """
    Generates random strings with unicode symbol.
    Possible Values in VAL_UNICOD (look in constanta ↑)
    :param size: size of returned text
    :param random_size: if True, return random size [0:size]
    :return: unicode text
    """
    if random_size:
        size = randint(0, size)
    result = ''
    for s in range(size):
        result += VAL_UNICOD[randint(0, VAL_UNICODE_LEN)]
    return result


def random_text(size: int = 1, random_size=False) -> str:
    """
    Generates random strings.
    Possible Values in VAL (look in constanta ↑)
    :param size: size of returned text
    :param random_size: if True, return random size [0:size]
    :return: text
    """
    if random_size:
        size = randint(0, size)
    result = ''
    for s in range(size):
        result += VAL[randint(0, VAL_LEN)]
    return result


def random_float(a: float, b: float) -> float:
    """
    :return random float with 14 digit after coma
    :param a: start digit
    :param b: end digit
    """
    return random.uniform(a, b)


def random_datetime(a: datetime, b: datetime):
    """
    :param a: start datetime
    :param b: end datetime
    :return: random datetime with timezone of 'a' parameter
    """
    return datetime.fromtimestamp(random_float(a.timestamp(), b.timestamp()), tz=a.tzinfo)


def random_list_element(array: list):
    """
    :param array: list of elements
    :return: random element of array
    """
    return array[randint(0, len(array) - 1)]


def random_bool() -> bool:
    """
    :return: return random bool value
    """
    return bool(randint(0, 1))
