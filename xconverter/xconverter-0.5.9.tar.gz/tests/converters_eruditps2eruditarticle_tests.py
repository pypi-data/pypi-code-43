import unittest
import os
import io

from lxml import etree

from converter import converters

APP_PATH = os.path.dirname(os.path.realpath(__file__))


class TestEruditPS2EruditAticle(unittest.TestCase):

    def setUp(self):

        self.conv = converters.EruditPS2EruditArticle(
            source=APP_PATH + '/fixtures/eruditps/document_eruditps.xml'
        )

        self.xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

    def test_text_encadre(self):
        inputxml = """
            <article xml:lang="fr" xmlns:xlink="http://www.w3.org/1999/xlink">
                <body>
                    <sec>
                        <boxed-text content-type="frame" id="en1">
                            <label>Encadré 1</label>
                            <caption xml:lang="fr">
                                <title>Pierre Harvey</title>
                            </caption>
                            <sec>
                                <fig id="fi4">
                                    <caption xml:lang="fr">
                                        <title>PIERRE HARVEY, Président de            la SCSE en 1964-65; un de ses membres fondateurs; Études à l’Université de Paris 1949-51;            Professeur d’économie à HEC 1951-1987, Directeur de HEC Montréal 1982-1986. Entrevue à            Montréal en janvier 2011.</title>
                                    </caption>
                                    <graphic id="im6" xlink:href="1861201n.jpg" position="float" content-type="figure"/>
                                </fig>
                                <p>Les années soixante sont bien loin mais avec son            excellente mémoire et son vif intérêt pour la chose historique, Pierre Harvey avait            conservé beaucoup de souvenirs. Ainsi, il se rappelle qu’une grande partie de la réunion            de fondation de la SCSE en octobre 1960 a porté sur l’appellation : des heures de            discussion, en particulier autour de l’adjectif « canadienne ». Tout le monde s’entendait            sur le caractère francophone du regroupement d’économistes à créer; il restait à            déterminer si l’on allait le qualifier de canadien, canadien-français,            québécois…</p>
                                <p>Il faut se rappeler qu’à cette époque, l’Université            Laval, par l’intermédiaire de certains des membres les plus en vue de son corps            professoral, était perçue comme très clairement fédéraliste alors qu’à HEC, le            nationalisme canadien-français, comme l’on disait à l’époque, ralliait, avec une ferveur            plus ou moins intense selon les individus, la majorité du corps professoral, des            économistes en particulier. L’assemblée procéda à un vote sur la question du nom et les            représentants de l’Université Laval l’emportèrent : le nom serait [Association canadienne            des économistes], un peu sur le modèle de l’Institut canadien des affaires publiques de            P.E. Trudeau. À cette opposition Laval-HEC, on doit ajouter les tensions qui opposaient            l’Université de Montréal à HEC à propos de l’enseignement de l’économie. Plus qu’une            querelle sur le caractère « scientifique » de l’enseignement dispensé dans les deux            établissements, c’était le droit de HEC à un tel enseignement qui faisait problème : le            département de sciences économiques considérait qu’avec son enseignement de science            économique, HEC débordait son domaine de compétence et empiétait sur celui de la faculté            de sciences sociales, nonobstant l’ancienneté de la présence de cette science dans le            curriculum de HEC. Un conflit qui allait mettre du temps à s’éteindre.</p>
                                <p>Au moment de la création de la SCSE en 1960 et pour            une bonne partie de cette décennie, il y avait très très peu d’économistes dans la            fonction publique québécoise et pas d’économistes francophones à Ottawa. Des économistes            dans les grandes entreprises et les banques, non plus. Pierre Harvey croit que l’origine            du métier d’économiste au Québec vient de la Commission d’enquête sur les problèmes            constitutionnels, la Commission Tremblay. Il se souvient encore que Duplessis avait dit :            « des avocats, j’en connais en masse; des économistes, j’en connais rien qu’un. C’est            François-Albert Angers, une maudite tête de cochon, j’en veux pas            d’autre ».</p>
                            </sec>
                        </boxed-text>
                    </sec>
                </body>
            </article>
        """

        conv = converters.EruditPS2EruditArticle(io.BytesIO(inputxml.encode('utf-8')))
        self.xml = conv.transform(lxml_etree=True, remove_namespace=True)

        expected = """
            <corps xmlns:xlink="http://www.w3.org/1999/xlink">
                <section1>
                    <encadre id="en1">
                        <no>Encadré 1</no>
                        <legende lang="fr">
                            <titre>Pierre Harvey</titre>
                        </legende>
                        <section1>
                            <figure id="fi4">
                                <legende lang="fr">
                                    <titre>PIERRE HARVEY, Président de            la SCSE en 1964-65; un de ses membres fondateurs; Études à l’Université de Paris 1949-51;            Professeur d’économie à HEC 1951-1987, Directeur de HEC\xa0Montréal 1982-1986. Entrevue à            Montréal en janvier 2011.</titre>
                                </legende>
                                <objetmedia flot="bloc">
                                    <image  typeimage="figure" xlink:type="simple" id="im6" xlink:href="1861201n.jpg"/>
                                </objetmedia>
                            </figure>
                            <alinea>Les années soixante sont bien loin mais avec son            excellente mémoire et son vif intérêt pour la chose historique, Pierre Harvey avait            conservé beaucoup de souvenirs. Ainsi, il se rappelle qu’une grande partie de la réunion            de fondation de la SCSE en octobre 1960 a porté sur l’appellation\xa0: des heures de            discussion, en particulier autour de l’adjectif «\xa0canadienne\xa0». Tout le monde s’entendait            sur le caractère francophone du regroupement d’économistes à créer; il restait à            déterminer si l’on allait le qualifier de canadien, canadien-français,            québécois…</alinea>
                            <alinea>Il faut se rappeler qu’à cette époque, l’Université            Laval, par l’intermédiaire de certains des membres les plus en vue de son corps            professoral, était perçue comme très clairement fédéraliste alors qu’à HEC, le            nationalisme canadien-français, comme l’on disait à l’époque, ralliait, avec une ferveur            plus ou moins intense selon les individus, la majorité du corps professoral, des            économistes en particulier. L’assemblée procéda à un vote sur la question du nom et les            représentants de l’Université Laval l’emportèrent\xa0: le nom serait [Association canadienne            des économistes], un peu sur le modèle de l’Institut canadien des affaires publiques de            P.E. Trudeau. À cette opposition Laval-HEC, on doit ajouter les tensions qui opposaient            l’Université de Montréal à HEC à propos de l’enseignement de l’économie. Plus qu’une            querelle sur le caractère «\xa0scientifique\xa0» de l’enseignement dispensé dans les deux            établissements, c’était le droit de HEC à un tel enseignement qui faisait problème\xa0: le            département de sciences économiques considérait qu’avec son enseignement de science            économique, HEC débordait son domaine de compétence et empiétait sur celui de la faculté            de sciences sociales, nonobstant l’ancienneté de la présence de cette science dans le            curriculum de HEC. Un conflit qui allait mettre du temps à s’éteindre.</alinea>
                            <alinea>Au moment de la création de la SCSE en 1960 et pour            une bonne partie de cette décennie, il y avait très très peu d’économistes dans la            fonction publique québécoise et pas d’économistes francophones à Ottawa. Des économistes            dans les grandes entreprises et les banques, non plus. Pierre Harvey croit que l’origine            du métier d’économiste au Québec vient de la Commission d’enquête sur les problèmes            constitutionnels, la Commission Tremblay. Il se souvient encore que Duplessis avait dit\xa0:            «\xa0des avocats, j’en connais en masse; des économistes, j’en connais rien qu’un. C’est            François-Albert Angers, une maudite tête de cochon, j’en veux pas            d’autre\xa0».</alinea>
                        </section1>
                    </encadre>
                </section1>
            </corps>
        """

        result = self.xml.find("corps")
        self.maxDiff = None
        parser = etree.XMLParser(remove_blank_text=True)
        self.assertEqual(
            etree.tostring(result),
            etree.tostring(etree.fromstring(expected, parser=parser))
        )

    def test_sub_sections(self):
        inputxml = """
            <article>
                <body>
                    <sec>
                        <title>Section 1</title>
                        <p>Text</p>
                        <sec>
                            <title>Section 2</title>
                            <p>Text</p>
                            <sec>
                                <title>Section 3</title>
                                <p>Text</p>
                                <sec>
                                    <title>Section 4</title>
                                    <p>Text</p>
                                    <sec>
                                        <title>Section 5</title>
                                        <p>Text</p>
                                        <sec>
                                            <title>Section 6</title>
                                            <p>Text</p>
                                        </sec>
                                    </sec>
                                </sec>
                            </sec>
                        </sec>
                    </sec>
                </body>
            </article>
        """

        conv = converters.EruditPS2EruditArticle(io.BytesIO(inputxml.encode('utf-8')))
        self.xml = conv.transform(lxml_etree=True, remove_namespace=True)

        expected = """
            <corps>
                <section1>
                    <titre>Section 1</titre>
                    <para id="pa0">
                        <no>pa0</no>
                        <alinea>Text</alinea>
                    </para>
                    <section2>
                        <titre>Section 2</titre>
                        <para id="pa0">
                            <no>pa0</no>
                            <alinea>Text</alinea>
                        </para>
                        <section3>
                            <titre>Section 3</titre>
                            <para id="pa0">
                                <no>pa0</no>
                                <alinea>Text</alinea>
                            </para>
                            <section4>
                                <titre>Section 4</titre>
                                <para id="pa0">
                                    <no>pa0</no>
                                    <alinea>Text</alinea>
                                </para>
                                <section5>
                                    <titre>Section 5</titre>
                                    <para id="pa0">
                                        <no>pa0</no>
                                        <alinea>Text</alinea>
                                    </para>
                                    <section6>
                                        <titre>Section 6</titre>
                                        <para id="pa0">
                                            <no>pa0</no>
                                            <alinea>Text</alinea>
                                        </para>
                                    </section6>
                                </section5>
                            </section4>
                        </section3>
                    </section2>
                </section1>
            </corps>
        """

        result = self.xml.find("corps")

        self.maxDiff = None
        parser = etree.XMLParser(remove_blank_text=True)
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            etree.tostring(etree.fromstring(expected, parser=parser), encoding='utf-8').decode('utf-8')
        )

    def test_text_formating(self):
        inputxml = """
            <article>
                <body>
                    <sec>
                        <title>Testing text formating convertions</title>
                        <p>
                            <bold>bold</bold>
                            <italic>italic</italic>
                            <underline>underline</underline>
                            <overline>overline</overline>
                            <strike>strike</strike>
                            <sc>smallcaps</sc>
                            <styled-content style-type="text-uppercase">uppercase</styled-content>
                            <styled-content style-type="text-boxed">boxed</styled-content>
                            <styled-content style-type="text-bigger">bigger</styled-content>
                            <styled-content style-type="text-smaller">smaller</styled-content>
                            <monospace>monospace</monospace>
                            <sub>sub</sub>
                            <sup>sup</sup>
                        </p>
                    </sec>
                </body>
            </article>
        """

        conv = converters.EruditPS2EruditArticle(io.BytesIO(inputxml.encode('utf-8')))
        self.xml = conv.transform(lxml_etree=True, remove_namespace=True)

        expected = """
            <corps>
                <section1>
                    <titre>Testing text formating convertions</titre>
                    <para id="pa0">
                        <no>pa0</no>
                        <alinea>
                            <marquage typemarq="gras">bold</marquage>
                            <marquage typemarq="italique">italic</marquage>
                            <marquage typemarq="souligne">underline</marquage>
                            <marquage typemarq="surlignage">overline</marquage>
                            <marquage typemarq="barre">strike</marquage>
                            <marquage typemarq="petitecap">smallcaps</marquage>
                            <marquage typemarq="majuscule">uppercase</marquage>
                            <marquage typemarq="filet">boxed</marquage>
                            <marquage typemarq="tailleg">bigger</marquage>
                            <marquage typemarq="taillep">smaller</marquage>
                            <marquage typemarq="espacefixe">monospace</marquage>
                            <indice>sub</indice>
                            <exposant>sup</exposant>
                        </alinea>
                    </para>
                </section1>
            </corps>
        """

        result = self.xml.find("corps")

        self.maxDiff = None
        parser = etree.XMLParser(remove_blank_text=True)
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            etree.tostring(etree.fromstring(expected, parser=parser), encoding='utf-8').decode('utf-8')
        )

    def test_issue_notes(self):

        result = self.xml.find("admin/numero/notegen[@porteenoteg='numero']")

        expected = b"""<notegen xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" porteenoteg="numero" lang="fr"><titre>Issue Notes</titre><alinea>Editor notes about the <marquage typemarq="italique">issue</marquage>...</alinea></notegen>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_article_notes(self):

        result = self.xml.find("liminaire/notegen[@porteenoteg='article']")

        expected = b"""<notegen xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" porteenoteg="article" lang="fr"><titre>Article Notes</titre><alinea>Editor notes about the <marquage typemarq="italique">article</marquage>...</alinea></notegen>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_article_issue_id(self):

        issue_id = self.xml.find('admin/numero').get('id')
        self.assertEqual(issue_id, 'approchesind01463')

    def test_article_issue_seq_1(self):
        """
        Data Structure has:
            <article-meta>
                ...
                <volume>1</volume>
                <issue seq="6">1</volume>
                ...
            </article-meta>
        """

        seq = self.xml.find('.').get('ordseq')

        self.assertEqual(seq, '6')

    def test_article_issue_seq_2(self):
        """
        Data Structure has:
            ...
            <article-meta>
                ...
                <volume seq="6">1</volume>
                ...
            </article-meta>
            ...
        """
        volume = self.conv.source_etree.find("front/article-meta/volume")
        volume.set('seq', '6')
        num = self.conv.source_etree.find("front/article-meta/issue")
        num.getparent().remove(num)

        custom_xml = self.conv.transform(lxml_etree=True)

        seq = custom_xml.find('.').get('ordseq')

        self.assertEqual(seq, '6')

    def test_article_issue_seq_3(self):
        """
        Data Structure has:
            ...
            <article-meta>
                ...
                <issue seq="6">1</issue>
                ...
            </article-meta>
            ...
        """
        volume = self.conv.source_etree.find("front/article-meta/volume")
        volume.getparent().remove(volume)

        custom_xml = self.conv.transform(lxml_etree=True)

        seq = custom_xml.find('.').get('ordseq')

        self.assertEqual(seq, '6')

    def test_article_element_attributes(self):

        typeart = self.xml.find('.').get('typeart')
        self.assertEqual(typeart, 'research-article')

        lang = self.xml.find('.').get('lang')
        self.assertEqual(lang, 'fr')

    def test_journal_id_erudit(self):

        result = self.xml.find("admin/revue").get('id')

        self.assertEqual(result, 'approchesind0522')

    def test_journal_title(self):

        result = self.xml.find("admin/revue/titrerev").text

        self.assertEqual(result, 'Approches inductives')

    def test_journal_subtitle(self):

        result = self.xml.find("admin/revue/sstitrerev").text

        self.assertEqual(result, 'Travail intellectuel et construction des connaissances')

    def test_abbrev_journal_title(self):

        result = self.xml.find("admin/revue/titrerevabr").text

        self.assertEqual(result, 'approchesind')

    def test_issns(self):

        result = self.xml.find("admin/revue/idissnnum").text

        self.assertEqual(result, '2292-0005')

    def test_issns_ppub_epub(self):

        other_issn = etree.Element('issn')
        other_issn.set('pub-type', 'ppub')
        other_issn.text = '1234-4321'

        self.conv.source_etree.find("front/journal-meta").append(other_issn)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("admin/revue/idissnnum").text
        self.assertEqual(result, '2292-0005')

        result = custom_xml.find("admin/revue/idissn").text
        self.assertEqual(result, '1234-4321')

    def test_journal_contrib_group_manager(self):

        result_surname = [i.text for i in self.xml.xpath('admin/revue/directeur//nomfamille')]
        result_givennames = [i.text for i in self.xml.xpath('admin/revue/directeur//prenom')]

        self.assertEqual(result_surname, ['Luckerhoff', 'Guillemette'])
        self.assertEqual(result_givennames, ['Jason', 'François'])

    def test_journal_contrib_group_editeur(self):

        result_surname = [i.text for i in self.xml.xpath('admin/revue/redacteurchef//nomfamille')]
        result_givennames = [i.text for i in self.xml.xpath('admin/revue/redacteurchef//prenom')]

        self.assertEqual(result_surname, ['Luckerhoff', 'Guillemette'])
        self.assertEqual(result_givennames, ['Jason', 'François'])

    def test_publisher_name(self):

        result = self.xml.find("admin/editeur/nomorg").text

        self.assertEqual(result, 'Université du Québec à Trois-Rivières')

    def test_article_meta_article_id_doi(self):

        result = self.xml.find("admin/infoarticle/idpublic[@scheme='doi']").text

        self.assertEqual(result, '10.7202/1025748ar')

    def test_article_meta_article_id_publisher(self):

        result = self.xml.find('.').get("idproprio")

        self.assertEqual(result, '1025748ar')

    def test_article_meta_title_group_article_categories_level_1(self):

        result = self.xml.find(
            "liminaire/grtitre/surtitre"
        ).text

        self.assertEqual(
            result,
            'Articles'
        )

    def test_article_meta_title_group_article_categories_level_2(self):

        result = self.xml.find(
            "liminaire/grtitre/surtitre2"
        ).text

        self.assertEqual(
            result,
            'Review Articles'
        )

    def test_article_meta_title_group_article_categories_level_3(self):

        result = self.xml.find(
            "liminaire/grtitre/surtitre3"
        ).text

        self.assertEqual(
            result,
            'Report'
        )

    def test_article_meta_title_group_article_categories_trans_level_1(self):

        result = self.xml.find(
            "liminaire/grtitre/surtitreparal[@lang='en']"
        ).text

        self.assertEqual(
            result,
            'Articles english'
        )

    def test_article_meta_title_group_article_categories_trans_level_2(self):

        result = self.xml.find(
            "liminaire/grtitre/surtitreparal2[@lang='en']"
        ).text

        self.assertEqual(
            result,
            'Review Articles english'
        )

    def test_article_meta_title_group_article_categories_trans_level_3(self):

        result = self.xml.find(
            "liminaire/grtitre/surtitreparal3[@lang='en']"
        ).text

        self.assertEqual(
            result,
            'Report english'
        )

    def test_article_meta_title_group_title(self):

        result = self.xml.find("liminaire/grtitre/titre")

        expected = '<titre xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">« Chantez au Seigneur un chant nouveau… » (Ps.95.1) : le portrait de la musique <marquage typemarq="italique">rock</marquage> chrétienne</titre>'

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_product(self):

        result = self.xml.find("liminaire/grtitre/trefbiblio")

        expected = '<trefbiblio xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><marquage typemarq="petitecap">Bornand</marquage>, Marie, <marquage typemarq="italique">Témoignage et fiction. Les récits de rescapés dans la littérature de langue française (1945-2000)</marquage>, Genève, Librairie Droz, 2004.</trefbiblio>'

        self.maxDiff = None
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_subtitle(self):

        result = self.xml.find(
            "liminaire/grtitre/sstitre"
        )

        expected = '<sstitre xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Article <marquage typemarq="italique">Subtitle</marquage></sstitre>'
        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_translated_title(self):

        result = self.xml.find(
            "liminaire/grtitre/titreparal[@lang='en']"
        )

        expected = """<titreparal xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" lang="en">Translated title in <marquage typemarq="italique">english</marquage></titreparal>"""

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_translated_subtitle(self):

        result = self.xml.find(
            "liminaire/grtitre/sstitreparal"
        )

        expected = """<sstitreparal xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" lang="en">Translated subtitle in <marquage typemarq="italique">english</marquage></sstitreparal>"""

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_contrib_group_num_authors(self):

        result = len(self.xml.xpath("liminaire/grauteur/auteur"))

        self.assertEqual(result, 5)

    def test_article_meta_contrib_group_content_surname(self):

        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur//nompers/nomfamille")]

        self.assertEqual(result, ['Falardeau', 'Perreault', 'François', 'Marine', 'Joseph'])

    def test_article_meta_contrib_group_content_given_names(self):

        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur//nompers/prenom")]

        self.assertEqual(result, ['Marie-Chantal', 'Stéphane', 'Rémy', 'Alexandre', 'Joseph'])

    def test_article_meta_contrib_group_content_autreprenom(self):

        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/nompers/autreprenom")]

        self.assertEqual(result, ['Marie'])

    def test_article_meta_contrib_group_content_prefixe(self):
        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/nompers/prefixe")]

        self.assertEqual(result, ['Sr.'])

    def test_article_meta_contrib_group_content_suffixe(self):
        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/nompers/suffixe")]

        self.assertEqual(result, ['Jr.'])

    def test_article_meta_contrib_group_content_nomorg(self):
        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/nomorg")]

        self.assertEqual(result, ['Théâtre Deuxième Réalité', 'ACME'])

    def test_article_meta_contrib_group_content_membre(self):
        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/membre/nompers/nomfamille")]

        self.assertEqual(result, ['Marine', 'Joseph'])

    def test_article_meta_contrib_email(self):

        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/courriel")]

        self.assertEqual(result, ['falardeau_fake@email.com'])

    def test_article_meta_contrib_ext_link(self):

        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/siteweb")]

        self.assertEqual(result, ['http://mysite.fake.com'])

    def test_article_meta_contrib_id(self):

        result = [i.get('id') for i in self.xml.xpath("liminaire/grauteur/auteur")]

        self.assertEqual(result, ['au1', 'au2', 'au3', 'au4', 'au5'])

    def test_article_meta_contrib_bio(self):

        result = self.xml.find("partiesann/grnotebio/notebio[@idrefs='au1']")

        self.maxDiff = None
        expected = """<notebio xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" id="nb1" idrefs="au1" lang="fr"><alinea><marquage typemarq="gras"><marquage typemarq="petitecap">Nancy R. Lange </marquage></marquage>a publié quatre recueils de poésie aux Écrits des Forges : <marquage typemarq="italique">Annabahébec, Femelle Faucon</marquage>, <marquage typemarq="italique">Reviens chanter rossignol </marquage>et <marquage typemarq="italique">Au seuil du bleu </marquage>(voir p. 95). Elle a publié des poèmes dans des collectifs (<marquage typemarq="italique">Château Bizarre</marquage>; voir p. 104) et en revue (<marquage typemarq="italique">Brèves littéraires </marquage>79, 80<marquage typemarq="italique">, Exit, Arcade, Estuaire, Moebius</marquage>). Elle a collaboré à <marquage typemarq="italique">Macadam tribu</marquage> et à des spectacles multimédia, dont <marquage typemarq="italique">Au seuil du bleu</marquage> (JMLDA et Sainte-Rose en Bleu 2009, des productions de la SLL; <marquage typemarq="italique">Brèves littéraires</marquage> 80). Elle a participé à deux autres activités de la SLL en 2010 : Journées de la culture (voir p. 36) et Sainte-Rose en Bleu (voir p. 15).</alinea></notebio>"""

        self.assertEqual(
            etree.tostring(result, encoding="UTF-8").decode('utf-8'),
            expected
        )

    def test_article_meta_aff(self):

        result = [i.text for i in self.xml.xpath("liminaire/grauteur/auteur/affiliation/alinea")]

        self.assertEqual(result, ['Université du Québec à Trois-Rivières', 'Test Affiliation'])

    def test_issue_pub_date(self):

        result = self.xml.find("admin/numero/pub/annee").text

        self.assertEqual(result, '2014')

    def test_issue_pub_date_season(self):

        result = self.xml.find("admin/numero/pub/periode").text

        self.assertEqual(result, 'automne')

    def test_article_pub_date(self):

        result = self.xml.find("admin/numero/pubnum/date").text

        self.assertEqual(result, '2014-06-26')

    def test_article_pub_date_publication_format(self):

        result = self.xml.find("admin/numero/pubnum/date").get('typedate')

        self.assertEqual(result, 'publication')

    def test_article_pub_date_publication_format_print(self):
        item = self.conv.source_etree.find("front/article-meta/pub-date[@date-type='pub']")
        item.set('publication-format', 'ppub')

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("admin/numero/pubnum/date").get('typedate')

        self.assertEqual(result, 'pubpapier')

    def test_article_issue_volume(self):

        result = self.xml.find("admin/numero/volume").text

        self.assertEqual(result, '1')

    def test_article_issue_number(self):

        result = self.xml.find("admin/numero/nonumero").text

        self.assertEqual(result, '1')

    def test_article_issue_title(self):

        result = self.xml.find("admin/numero/grtheme/theme").text

        self.assertEqual(result, 'Approches inductives en communication sociale')

    def test_article_fpage(self):

        result = self.xml.find("admin/infoarticle/pagination/ppage").text

        self.assertEqual(result, '125')

    def test_article_lpage(self):

        result = self.xml.find("admin/infoarticle/pagination/dpage").text

        self.assertEqual(result, '148')

    def test_permissions_copyright_statement(self):

        result = self.xml.find("admin/droitsauteur[1]/declaration")

        expected = """<declaration xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Tous droits réservés © Approches inductives, 2014</declaration>"""

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_permissions_copyright_year(self):

        result = self.xml.find("admin/droitsauteur/annee").text

        self.assertEqual(result, "2014")

    def test_permissions_copyright_holder(self):

        result = self.xml.find("admin/droitsauteur/nomorg").text

        self.assertEqual(result, "Approches inductives")

    def test_permissions_copyright_license_link(self):

        result = self.xml.find("admin/droitsauteur/liensimples").get('{http://www.w3.org/1999/xlink}href')

        self.assertEqual(result, "http://creativecommons.org/licenses/by-sa/3.0/")

    def test_permissions_copyright_license_link_image(self):

        result = self.xml.find("admin/droitsauteur/objetmedia/image").get('{http://www.w3.org/1999/xlink}href')


        self.assertEqual(result, "http://i.creativecommons.org/l/by-sa/3.0/88x31.png")

    def test_abstract(self):

        result = self.xml.find("liminaire/resume[@lang='fr']")

        expected = """<resume xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" lang="fr"><titre>Resume</titre><alinea>Le but de cet article est de présenter les raisons du choix d’une approche inductive, plutôt qu’une approche déductive, afin d’étudier la musique rock chrétienne. Cette étude dresse un portrait des chansons les plus populaires de la musique rock chrétienne tout en décrivant quantitativement les éléments structurels de ces dernières. Afin de réaliser ce projet, nous avons répertorié tous les numéros un du palmarès américain <marquage typemarq="italique">Christian Songs</marquage> depuis sa création en 2003\xa0jusqu’à la fin de l’année 2011, soit 65\xa0chansons. Le portrait de la musique rock chrétienne se décline en onze catégories dont les plus récurrentes sont la dévotion, la présence de Dieu et l’espoir. Cette musique est aussi chantée majoritairement par des hommes et se caractérise par un rythme lent.</alinea></resume>"""

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_trans_abstract(self):

        result = self.xml.find("liminaire/resume[@lang='en']")

        expected = """<resume xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" lang="en"><titre>Abstract</titre><alinea>Abstract translation sample.</alinea></resume>"""

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_keywords(self):

        result = self.xml.findall("liminaire/grmotcle[@lang='fr']/motcle")

        result = ';'.join([i.text for i in result])

        expected = "Étude mixte;méthodologie inductive;musique rock chrétienne;analyse de contenu"

        self.assertEqual(result, expected)

    def test_keywords_trans(self):

        result = self.xml.findall("liminaire/grmotcle[@lang='en']/motcle")

        result = ';'.join([i.text for i in result])

        expected = "keyword in english"

        self.assertEqual(result, expected)

    def test_keywords_title(self):

        result = self.xml.findall("liminaire/grmotcle/titre")

        result = ';'.join([i.text for i in result])

        expected = "Motclés;Keywords"

        self.assertEqual(result, expected)

    def test_ref_count(self):

        result = self.xml.find("admin/infoarticle/nbrefbiblio").text

        self.assertEqual(result, '61')

    def test_table_count(self):

        result = self.xml.find("admin/infoarticle/nbtabl").text

        self.assertEqual(result, '6')

    def test_fig_count(self):

        result = self.xml.find("admin/infoarticle/nbfig").text

        self.assertEqual(result, '3')

    def test_equation_count(self):

        result = self.xml.find("admin/infoarticle/nbeq").text

        self.assertEqual(result, '3')

    def test_page_count_ppage_absent(self):
        articlemeta = self.conv.source_etree.find("front/article-meta")
        fpage = articlemeta.find('fpage')
        articlemeta.remove(fpage)

        custom_xml = self.conv.transform(lxml_etree=True)

        result = custom_xml.find("admin/infoarticle/nbpage")

        self.assertEqual(result, None)

    def test_page_count_dpage_absent(self):
        articlemeta = self.conv.source_etree.find("front/article-meta")
        lpage = articlemeta.find('lpage')
        articlemeta.remove(lpage)

        custom_xml = self.conv.transform(lxml_etree=True)

        result = custom_xml.find("admin/infoarticle/nbpage")

        self.assertEqual(result, None)

    def test_page_count_ppage_bigger_dpage_absent(self):
        fpage = self.conv.source_etree.find("front/article-meta/fpage")
        lpage = self.conv.source_etree.find("front/article-meta/lpage")
        fpage.text = '120'
        lpage.text = '100'

        custom_xml = self.conv.transform(lxml_etree=True)

        result = custom_xml.find("admin/infoarticle/nbpage")

        self.assertEqual(result, None)

    def test_page_count_ppage_not_number(self):
        fpage = self.conv.source_etree.find("front/article-meta/fpage")
        fpage.text = 'a'

        custom_xml = self.conv.transform(lxml_etree=True)

        result = custom_xml.find("admin/infoarticle/nbpage")

        self.assertEqual(result, None)

    def test_page_count_dpage_not_number(self):
        lpage = self.conv.source_etree.find("front/article-meta/lpage")
        lpage.text = 'a'

        custom_xml = self.conv.transform(lxml_etree=True)

        result = custom_xml.find("admin/infoarticle/nbpage")

        self.assertEqual(result, None)

    def test_page_count(self):

        result = self.xml.find("admin/infoarticle/nbpage").text

        self.assertEqual(result, '24')

    def test_paragraph_count(self):

        result = self.xml.find("admin/infoarticle/nbpara").text

        self.assertEqual(result, '36')

    def test_notes_count(self):

        result = self.xml.find("admin/infoarticle/nbnote").text

        self.assertEqual(result, '7')

    def test_words_count(self):

        result = self.xml.find("admin/infoarticle/nbmot").text

        self.assertEqual(result, '4808')

    def test_videos_count(self):

        result = self.xml.find("admin/infoarticle/nbvideo").text

        self.assertEqual(result, '0')

    def test_audios_count(self):

        result = self.xml.find("admin/infoarticle/nbaudio").text

        self.assertEqual(result, '0')

    def test_image_count(self):

        result = self.xml.find("admin/infoarticle/nbimage").text

        self.assertEqual(result, '8')

    def test_figure_count(self):

        result = self.xml.find("admin/infoarticle/nbfig").text

        self.assertEqual(result, '3')

    def test_ack(self):

        result = self.xml.find("partiesann/merci")

        self.maxDiff = None

        expected = """<merci xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><titre>Merci</titre><alinea>Cet <marquage typemarq="italique">article</marquage> est une version modifiée d’un texte présenté au séminaire HPES du CLERSE (Université Lille I). Nous remercions Vincent Duwicquet, Jordan Melmiès et Jonathan Marie pour leurs commentaires, Malika Riboudt pour l’assistance technique sur Maple, Marc Lavoie et Louis-Philippe Rochon pour leurs conseils. Nous tenons également à faire part de notre gratitude aux rapporteurs de la revue pour leurs remarques pertinentes. Néanmoins, nous demeurons seuls responsables des erreurs pouvant subsister.</alinea></merci>"""

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_ack_titre(self):

        result = self.xml.find("partiesann/merci/titre").text

        self.assertEqual(result, 'Merci')

    def test_xref_fn(self):

        result = ['-'.join([i.get('typeref'), i.get('idref'), i.text]) for i in self.xml.findall("corps//renvoi[@typeref='note']")]

        expected = ['note-no1-1', 'note-no2-2', 'note-no3-3', 'note-no4-4', 'note-no5-5', 'note-no6-6']

        self.assertEqual(result, expected)

    def test_table_wrap_label(self):

        result = self.xml.find("corps//tableau[@id='ta1']/no").text

        self.assertEqual(
            result.strip(),
            'Tableau 1'
        )

    def test_table_wrap_caption(self):

        result = self.xml.find("corps//tableau[@id='ta1']/legende/titre").text

        self.assertEqual(
            result.strip(),
            'Synthèse des analyses de contenu aux États-Unis, 1969-2006'
        )

    def test_table_wrap_table_note(self):

        result = self.xml.find("corps//tableau[@id='ta1']/notetabl[@id='tnt1']").text

        self.assertEqual(
            result.strip(),
            'Sample of table notes'
        )

    def test_table_wrap_with_text_table(self):

        result = self.xml.find("corps//tableau[@id='ta6']/tabtexte")

        expected = """<tabtexte xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><tabgrcol><tabcol alignh="gauche" alignv="centre"/><tabcol alignh="centre"/><tabcol alignh="centre"/><tabcol alignh="centre"/></tabgrcol><tabentete><tabligne><tabcellulee alignh="centre" alignv="centre"><alinea>Maisons</alinea></tabcellulee><tabcellulee alignh="centre"><alinea>Secteur urbain</alinea></tabcellulee><tabcellulee alignh="centre"><alinea>Secteur rural</alinea></tabcellulee><tabcellulee alignh="centre"><alinea>Total</alinea></tabcellulee></tabligne></tabentete><tabgrligne><tabligne><tabcelluled alignh="gauche" alignv="centre"><alinea>Détruites</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1888</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1198</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>3086</alinea></tabcelluled></tabligne><tabligne><tabcelluled alignh="gauche" alignv="centre"><alinea>Endommagées</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1342</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>297</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1639</alinea></tabcelluled></tabligne><tabligne><tabcelluled alignh="gauche" alignv="centre"><alinea>Sous-total</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>3230</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1495</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>4725</alinea></tabcelluled></tabligne><tabligne><tabcelluled alignh="gauche" alignv="centre"><alinea>Intactes</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1604</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>1191</alinea></tabcelluled><tabcelluled alignh="centre"><alinea>2795</alinea></tabcelluled></tabligne></tabgrligne><tabpied><tabligne><tabcelluled alignh="droite" alignv="centre"><alinea>Total</alinea></tabcelluled><tabcelluled alignh="droite"><alinea>4834</alinea></tabcelluled><tabcelluled alignh="droite"><alinea>2686</alinea></tabcelluled><tabcelluled alignh="droite"><alinea>7520</alinea></tabcelluled></tabligne></tabpied></tabtexte>"""

        self.maxDiff = None

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_table_wrap_attrib(self):

        result = self.xml.find("corps//tableau[@id='ta1']/source").text

        self.assertEqual(
            result.strip(),
            'Sample of source data'
        )

    def test_table_wrap_graphic(self):

        result = self.xml.find("corps//tableau[@id='ta1']/objetmedia")

        self.assertEqual(result.get('float').strip(), 'ligne')

        self.assertEqual(result.find('image').get('typeimage').strip(), 'tableau')

        self.assertEqual(result.find('image').get('{http://www.w3.org/1999/xlink}href').strip(), 'image_tableau_1.png')

    def test_figure_label(self):

        result = self.xml.find("corps//figure[@id='fi1']/no").text

        self.assertEqual(
            result.strip(),
            'Figure 1'
        )

    def test_figure_caption(self):

        result = self.xml.find("corps//figure[@id='fi1']/legende/titre").text

        self.assertEqual(
            result.strip(),
            'Modèle des valeurs de Schwartz (1992)'
        )

    def test_figure_alt_text(self):

        result = self.xml.find("corps//figure[@id='fi1']/notefig").text

        self.assertEqual(
            result.strip(),
            'Sample of figure notes'
        )

    def test_figure_attrib(self):

        result = self.xml.find("corps//figure[@id='fi1']/source").text

        self.assertEqual(
            result.strip(),
            'Sample of source data'
        )

    def test_fig_graphic(self):

        result = self.xml.find("corps//figure[@id='fi1']/objetmedia")

        self.assertEqual(result.get('flot').strip(), 'bloc')

        self.assertEqual(result.find('image').get('typeimage').strip(), 'figure')

        self.assertEqual(result.find('image').get('{http://www.w3.org/1999/xlink}href').strip(), 'image_figure_1.png')

    def test_epigraph(self):

        result = self.xml.find("corps/epigraphe")

        expected = """<epigraphe xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><alinea>Un jour, tout sera bien, voilà notre espérance :</alinea><alinea>Tout est bien aujourd’hui, voilà l’illusion.</alinea><source>Voltaire, <marquage typemarq="italique">Le désastre de Lisbonne</marquage></source></epigraphe>"""

        self.assertEqual(
            etree.tostring(result, encoding="UTF-8").decode('UTF-8'),
            expected
        )
