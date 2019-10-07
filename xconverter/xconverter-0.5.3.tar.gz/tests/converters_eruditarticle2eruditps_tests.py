import unittest
import os
import io

from lxml import etree

from converter import converters

APP_PATH = os.path.dirname(os.path.realpath(__file__))


class TestEruditArticle2EruditPS(unittest.TestCase):

    def setUp(self):

        self.conv = converters.EruditArticle2EruditPS(
            source=APP_PATH + '/fixtures/eruditarticle/document_eruditarticle.xml'
        )

        self.xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

    def test_text_encadre(self):
        inputxml = """
            <article lang="fr" xmlns:xlink="http://www.w3.org/1999/xlink">
                <corps>
                    <section1>
                        <encadre id="en1" type="1">
                            <no>Encadré 1</no>
                            <legende lang="fr">
                                <titre>Pierre Harvey</titre>
                            </legende>
                            <section1 id="s1n3">
                                <figure id="fi4">
                                    <legende lang="fr">
                                        <titre>PIERRE HARVEY, Président de            la SCSE en 1964-65; un de ses membres fondateurs; Études à l’Université de Paris 1949-51;            Professeur d’économie à HEC 1951-1987, Directeur de HEC Montréal 1982-1986. Entrevue à            Montréal en janvier 2011.</titre>
                                    </legende>
                                    <objetmedia flot="bloc">
                                        <image xmlns:xlink="http://www.w3.org/1999/xlink" typeimage="figure" id="im6" xlink:type="simple" xlink:href="1861201n.jpg"/>
                                    </objetmedia>
                                </figure>
                                <alinea>Les années soixante sont bien loin mais avec son            excellente mémoire et son vif intérêt pour la chose historique, Pierre Harvey avait            conservé beaucoup de souvenirs. Ainsi, il se rappelle qu’une grande partie de la réunion            de fondation de la SCSE en octobre 1960 a porté sur l’appellation : des heures de            discussion, en particulier autour de l’adjectif « canadienne ». Tout le monde s’entendait            sur le caractère francophone du regroupement d’économistes à créer; il restait à            déterminer si l’on allait le qualifier de canadien, canadien-français,            québécois…</alinea>
                                <alinea>Il faut se rappeler qu’à cette époque, l’Université            Laval, par l’intermédiaire de certains des membres les plus en vue de son corps            professoral, était perçue comme très clairement fédéraliste alors qu’à HEC, le            nationalisme canadien-français, comme l’on disait à l’époque, ralliait, avec une ferveur            plus ou moins intense selon les individus, la majorité du corps professoral, des            économistes en particulier. L’assemblée procéda à un vote sur la question du nom et les            représentants de l’Université Laval l’emportèrent : le nom serait [Association canadienne            des économistes], un peu sur le modèle de l’Institut canadien des affaires publiques de            P.E. Trudeau. À cette opposition Laval-HEC, on doit ajouter les tensions qui opposaient            l’Université de Montréal à HEC à propos de l’enseignement de l’économie. Plus qu’une            querelle sur le caractère « scientifique » de l’enseignement dispensé dans les deux            établissements, c’était le droit de HEC à un tel enseignement qui faisait problème : le            département de sciences économiques considérait qu’avec son enseignement de science            économique, HEC débordait son domaine de compétence et empiétait sur celui de la faculté            de sciences sociales, nonobstant l’ancienneté de la présence de cette science dans le            curriculum de HEC. Un conflit qui allait mettre du temps à s’éteindre.</alinea>
                                <alinea>Au moment de la création de la SCSE en 1960 et pour            une bonne partie de cette décennie, il y avait très très peu d’économistes dans la            fonction publique québécoise et pas d’économistes francophones à Ottawa. Des économistes            dans les grandes entreprises et les banques, non plus. Pierre Harvey croit que l’origine            du métier d’économiste au Québec vient de la Commission d’enquête sur les problèmes            constitutionnels, la Commission Tremblay. Il se souvient encore que Duplessis avait dit :            « des avocats, j’en connais en masse; des économistes, j’en connais rien qu’un. C’est            François-Albert Angers, une maudite tête de cochon, j’en veux pas            d’autre ».</alinea>
                                <section2>
                                    <alinea>test</alinea>
                                </section2>
                            </section1>
                        </encadre>
                    </section1>
                </corps>
            </article>
        """

        conv = converters.EruditArticle2EruditPS(io.BytesIO(inputxml.encode('utf-8')))
        self.xml = conv.transform(lxml_etree=True, remove_namespace=True)

        expected = """
            <body xmlns:xlink="http://www.w3.org/1999/xlink">
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
                            <sec>
                                <p>test</p>
                            </sec>
                        </sec>
                    </boxed-text>
                </sec>
            </body>
        """

        result = self.xml.find("body")

        self.maxDiff = None
        parser = etree.XMLParser(remove_blank_text=True)
        self.assertEqual(
            etree.tostring(result, encoding='utf-8').decode('utf-8'),
            etree.tostring(etree.fromstring(expected, parser=parser), encoding='utf-8').decode('utf-8')
        )

    def test_text_formating(self):
        inputxml = """
            <article lang="fr">
                <corps>
                    <section1>
                        <titre>Testing text formating convertions</titre>
                        <para>
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
            </article>
        """

        conv = converters.EruditArticle2EruditPS(io.BytesIO(inputxml.encode('utf-8')))
        self.xml = conv.transform(lxml_etree=True, remove_namespace=True)

        expected = """
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
        """

        result = self.xml.find("body")

        self.maxDiff = None
        parser = etree.XMLParser(remove_blank_text=True)
        self.assertEqual(
            etree.tostring(result),
            etree.tostring(etree.fromstring(expected, parser=parser))
        )

    def test_issue_notes(self):

        result = self.xml.find("front/notes/sec[@sec-type='issue-note']")

        expected = b"""<sec xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" sec-type="issue-note" xml:lang="fr"><title>Issue Notes</title><p>Editor notes about the <italic>issue</italic>...</p></sec>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_article_notes(self):

        result = self.xml.find("front/notes/sec[@sec-type='article-note']")

        expected = b"""<sec xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" sec-type="article-note" xml:lang="fr"><title>Article Notes</title><p>Editor notes about the <italic>article</italic>...</p></sec>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_article_issue_id(self):

        seq = self.xml.find('front/article-meta/issue-id').text
        self.assertEqual(seq, 'approchesind01463')

    def test_article_issue_seq_1(self):
        """
        Data Structure has:
            ...
            <numero id="approchesind01463">
                <volume>1</volume>
                <nonumero>1</nonumero>
                ...
            </numero>
            ...
        """

        seq = self.xml.find('front/article-meta/issue').get('seq')
        self.assertEqual(seq, '6')

        seq = self.xml.find('front/article-meta/volume').get('seq')
        self.assertEqual(seq, None)

    def test_article_issue_seq_2(self):
        """
        Data Structure has:
            ...
            <numero id="approchesind01463">
                <volume>1</volume>
                ...
            </numero>
            ...
        """
        num = self.conv.source_etree.find("admin/numero/nonumero")
        num.getparent().remove(num)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        seq = custom_xml.find('front/article-meta/volume').get('seq')

        self.assertEqual(seq, '6')

    def test_article_issue_seq_3(self):
        """
        Data Structure has:
            ...
            <numero id="approchesind01463">
                <nonumero>1</nonumero>
                ...
            </numero>
            ...
        """
        num = self.conv.source_etree.find("admin/numero/volume")
        num.getparent().remove(num)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        seq = custom_xml.find('front/article-meta/issue').get('seq')

        self.assertEqual(seq, '6')

    def test_article_element_attributes(self):

        typeart = self.xml.find('.').get('article-type')
        self.assertEqual(typeart, 'research-article')

        lang = self.xml.find('.').get('{http://www.w3.org/XML/1998/namespace}lang')
        self.assertEqual(lang, 'fr')

    def test_journal_id_erudit(self):

        result = self.xml.find("front/journal-meta/journal-id[@journal-id-type='publisher-id']").text

        self.assertEqual(result, 'approchesind0522')

    def test_journal_title(self):

        result = self.xml.find("front/journal-meta/journal-title-group/journal-title").text

        self.assertEqual(result, 'Approches inductives')

    def test_journal_subtitle(self):

        result = self.xml.find("front/journal-meta/journal-title-group/journal-subtitle").text

        self.assertEqual(result, 'Travail intellectuel et construction des connaissances')

    def test_abbrev_journal_title(self):

        result = self.xml.find("front/journal-meta/journal-title-group/abbrev-journal-title").text

        self.assertEqual(result, 'approchesind')

    def test_issns(self):

        result = ';'.join(
            sorted(['%s-%s' % (i.get('pub-type'), i.text) for i in self.xml.xpath("front/journal-meta//issn")])
        )

        self.assertEqual(result, 'epub-2292-0005')

    def test_issns_ppub_epub(self):

        self.conv.source_etree.find("admin/revue").append(etree.Element('idissn'))
        self.conv.source_etree.find("admin/revue/idissn").text = '1234-4321'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = ';'.join(
            sorted(['%s-%s' % (i.get('pub-type'), i.text) for i in custom_xml.xpath("front/journal-meta//issn")])
        )

        self.assertEqual(result, 'epub-2292-0005;ppub-1234-4321')

    def test_journal_contrib_group_manager(self):

        result = self.xml.xpath("front/journal-meta/contrib-group[@content-type='manager']")

        result_surname = [i.text for i in result[0].xpath('.//surname')]
        result_givennames = [i.text for i in result[0].xpath('.//given-names')]

        self.assertEqual(result_surname, ['Luckerhoff', 'Guillemette'])
        self.assertEqual(result_givennames, ['Jason', 'François'])

    def test_journal_contrib_group_editeur(self):

        result = self.xml.xpath("front/journal-meta/contrib-group[@content-type='editor']")

        result_surname = [i.text for i in result[0].xpath('.//surname')]
        result_givennames = [i.text for i in result[0].xpath('.//given-names')]

        self.assertEqual(result_surname, ['Luckerhoff', 'Guillemette'])
        self.assertEqual(result_givennames, ['Jason', 'François'])

    def test_publisher_name(self):

        result = self.xml.find("front/journal-meta/publisher/publisher-name").text

        self.assertEqual(result, 'Université du Québec à Trois-Rivières')

    def test_article_meta_article_id_doi(self):

        result = ['%s-%s' % (i.get('pub-id-type'), i.text) for i in self.xml.xpath("front/article-meta/article-id")]

        self.assertEqual(result, ['doi-10.7202/1025748ar', 'publisher-id-1025748ar'])

    def test_article_meta_article_id_publisher(self):

        result = self.xml.find("front/article-meta/article-id[@pub-id-type='publisher-id']").text

        self.assertEqual(result, '1025748ar')

    def test_article_meta_title_group_article_categories_level_1(self):

        result = self.xml.find("front/article-meta/article-categories/subj-group/subject").text

        self.assertEqual(
            result,
            'Articles'
        )

    def test_article_meta_title_group_article_categories_level_2(self):

        result = self.xml.find("front/article-meta/article-categories/subj-group/subj-group/subject").text

        self.assertEqual(
            result,
            'Review Articles'
        )

    def test_article_meta_title_group_article_categories_level_3(self):

        result = self.xml.find(
            "front/article-meta/article-categories/subj-group/subj-group/subj-group/subject"
        ).text

        self.assertEqual(
            result,
            'Report'
        )

    def test_article_meta_title_group_article_categories_trans_level_1(self):

        result = self.xml.find("front/article-meta/article-categories/subj-group[@{http://www.w3.org/XML/1998/namespace}lang='en']/subject").text

        self.assertEqual(
            result,
            'Articles english'
        )

    def test_article_meta_title_group_article_categories_trans_level_2(self):

        result = self.xml.find(
            "front/article-meta/article-categories/subj-group[@{http://www.w3.org/XML/1998/namespace}lang='en']/subj-group/subject"
        ).text

        self.assertEqual(
            result,
            'Review Articles english'
        )

    def test_article_meta_title_group_article_categories_trans_level_3(self):

        result = self.xml.find(
            "front/article-meta/article-categories/subj-group[@{http://www.w3.org/XML/1998/namespace}lang='en']/subj-group/subj-group/subject"
        ).text

        self.assertEqual(
            result,
            'Report english'
        )

    def test_article_meta_title_group_title(self):

        result = self.xml.find("front/article-meta/title-group/article-title[@{http://www.w3.org/XML/1998/namespace}lang='fr']")
        self.maxDiff = None
        expected = '<article-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">« Chantez au Seigneur un chant nouveau… » (Ps.95.1) : le portrait de la musique <italic>rock</italic> chrétienne</article-title>'

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            expected
        )

    def test_article_meta_title_group_subtitle(self):

        result = self.xml.find(
            "front/article-meta/title-group/subtitle[@{http://www.w3.org/XML/1998/namespace}lang='fr']"
        )

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            '<subtitle xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">Article <italic>Subtitle</italic></subtitle>'
        )

    def test_article_meta_product(self):

        result = self.xml.find(
            "front/article-meta/product"
        )

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            '<product xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><related-object><sc>Bornand</sc>, Marie, <italic>Témoignage et fiction. Les récits de rescapés dans la littérature de langue française (1945-2000)</italic>, Genève, Librairie Droz, 2004.\n      </related-object></product>'
        )

    def test_article_meta_title_group_translated_title(self):

        result = self.xml.findall("front/article-meta/title-group//trans-title-group/trans-title")

        result = [etree.tostring(i) for i in result]

        expected = [
            b"""<trans-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated title in <italic>english</italic></trans-title>""",
            b"""<trans-title xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated title in <italic>portuguese</italic></trans-title>"""
        ]

        self.assertEqual(
            sorted(result),
            sorted(expected)
        )

    def test_article_meta_title_group_translated_subtitle(self):

        result = self.xml.findall(
            "front/article-meta/title-group//trans-title-group/trans-subtitle"
        )

        result = [etree.tostring(i) for i in result]
        expected = [
            b"""<trans-subtitle xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated subtitle in <italic>english</italic></trans-subtitle>""",
            b"""<trans-subtitle xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">Translated subtitle in <italic>portuguese</italic></trans-subtitle>"""
        ]
        self.assertEqual(
            sorted(result),
            sorted(expected)
        )

    def test_article_meta_contrib_group_num_authors(self):

        result = len(self.xml.xpath("front/article-meta/contrib-group/contrib"))

        self.assertEqual(result, 5)

    def test_article_meta_contrib_group_content(self):

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group//contrib/name/surname")]

        self.assertEqual(result, ['Falardeau', 'Perreault', 'François', 'Marine', 'Joseph'])

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group//contrib/name/given-names")]

        self.assertEqual(result, ['Marie-Chantal', 'Stéphane Marie', 'Rémy', 'Alexandre', 'Joseph'])

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group/contrib/name/suffix")]

        self.assertEqual(result, ['Jr.'])

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group/contrib/name/prefix")]

        self.assertEqual(result, ['Sr.'])

    def test_article_meta_contrib_group_contrib_author_alias(self):
        """
        Testing author having a alias.

        Input:
        <auteur id="au1">
            <nompers typenompers="usage">
                <prenom>Kurt</prenom>
                <nomfamille>Tucholsky</nomfamille>
            </nompers>
            <nompers typenompers="pseudonyme">
                <prenom>Peter Panter</prenom>
            </nompers>
        </auteur>
        """

        nompers = etree.Element('nompers', typenompers="pseudonyme")
        prenom = etree.Element('prenom')
        prenom.text = "Peter Panter"
        nomfamille = etree.Element('nomfamille')
        nomfamille.text = "The Peter"
        nompers.append(prenom)
        nompers.append(nomfamille)
        item = self.conv.source_etree.find("liminaire/grauteur/auteur[@id='au1']")
        item.append(nompers)
        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find(
            "front/article-meta/contrib-group/contrib/[@id='au1']/string-name[@content-type='alias']"
        ).text


        self.assertEqual(result, "Peter Panter The Peter")

    def test_article_meta_contrib_group_contrib_xref(self):

        result = [i.get('rid') for i in self.xml.xpath("front/article-meta/contrib-group//xref")]

        self.assertEqual(result, ['aff1', 'aff2', 'aff2', 'aff2'])

    def test_article_meta_contrib_email(self):

        result = [i.text for i in self.xml.xpath("front/article-meta/contrib-group/contrib/email")]

        self.assertEqual(result, ['falardeau_fake@email.com'])

    def test_article_meta_contrib_ext_link(self):

        result = [i.get('{http://www.w3.org/1999/xlink}href') for i in self.xml.xpath("front/article-meta/contrib-group/contrib/ext-link")]

        self.assertEqual(result, ['http://mysite.fake.com'])

    def test_article_meta_contrib_id(self):

        result = [i.get('id') for i in self.xml.xpath("front/article-meta/contrib-group/contrib")]

        self.assertEqual(result, ['au1', 'au2', 'au3', 'au4', 'au5'])

    def test_article_meta_contrib_bio(self):

        result = self.xml.xpath("front/article-meta/contrib-group/contrib[@id='au1']/bio")

        expected = b"""<bio xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr"><title>Auteur Bio</title><p><bold><sc>Nancy R. Lange </sc></bold>a publi&#233; quatre recueils de po&#233;sie aux &#201;crits des Forges : <italic>Annabah&#233;bec, Femelle Faucon</italic>, <italic>Reviens chanter rossignol </italic>et <italic>Au seuil du bleu </italic>(voir p. 95). Elle a publi&#233; des po&#232;mes dans des collectifs (<italic>Ch&#226;teau Bizarre</italic>; voir p. 104) et en revue (<italic>Br&#232;ves litt&#233;raires </italic>79, 80<italic>, Exit, Arcade, Estuaire, Moebius</italic>). Elle a collabor&#233; &#224; <italic>Macadam tribu</italic> et &#224; des spectacles multim&#233;dia, dont <italic>Au seuil du bleu</italic> (JMLDA et Sainte-Rose en Bleu 2009, des productions de la SLL; <italic>Br&#232;ves litt&#233;raires</italic> 80). Elle a particip&#233; &#224; deux autres activit&#233;s de la SLL en 2010 : Journ&#233;es de la culture (voir p. 36) et Sainte-Rose en Bleu (voir p. 15).\n        </p></bio>"""

        self.assertEqual(etree.tostring(result[0]), expected)

    def test_article_meta_aff(self):

        result = [i.text for i in self.xml.xpath("front/article-meta/aff/institution")]

        self.assertEqual(result, ['Université du Québec à Trois-Rivières', 'Test Affiliation'])

    def test_article_pub_date(self):

        result = []
        for item in self.xml.xpath("front/article-meta/pub-date[@date-type='pub']"):

            dat = '-'.join([
                item.find('year').text or '',
                item.find('month').text or '',
                item.find('day').text or '',
            ])
            result.append(dat)

        self.assertEqual(result, ['2014-06-26'])

    def test_article_pub_date_publication_format(self):

        item = self.conv.source_etree.find("admin/numero/pubnum/date")
        item.set('typedate', 'pubpapier')

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/pub-date[@date-type='pub']").get('publication-format')

        self.assertEqual(result, 'ppub')

    def test_article_pub_date_without_publication_format(self):

        item = self.conv.source_etree.find("admin/numero/pubnum/date")
        del item.attrib['typedate']
        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/pub-date[@date-type='pub']")

        self.assertTrue('publication-format' not in result.attrib)

    def test_article_issue_volume(self):

        result = self.xml.find("front/article-meta/volume").text

        self.assertEqual(result, '1')

    def test_article_issue_number(self):

        result = self.xml.find("front/article-meta/issue").text

        self.assertEqual(result, '1')

    def test_article_issue_title(self):

        result = self.xml.find("front/article-meta/issue-title").text

        self.assertEqual(result, 'Approches inductives en communication sociale')

    def test_article_fpage(self):

        result = self.xml.find("front/article-meta/fpage").text

        self.assertEqual(result, '125')

    def test_article_lpage(self):

        result = self.xml.find("front/article-meta/lpage").text

        self.assertEqual(result, '148')

    def test_permissions_copyright_statement_1(self):

        inputxml = """
            <admin>
                <droitsauteur>Tous droits réservés © <nomorg>Approches inductives</nomorg>, 2014</droitsauteur>
                <droitsauteur>
                    <liensimple xmlns:xlink="http://www.w3.org/1999/xlink" id="ls1" xlink:href="http://creativecommons.org/licenses/by-sa/3.0/" xlink:actuate="onRequest" xlink:show="replace" xlink:type="simple">
                        <objetmedia flot="ligne">
                            <image typeimage="forme" xlink:href="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" xlink:actuate="onLoad" xlink:show="embed" xlink:type="simple"/>
                        </objetmedia>
                    </liensimple>
                </droitsauteur>
            </admin>"""

        """<copyright-statement>Tous droits réservés © Approches Inductives, 2014</copyright-statement>"""

        parser = etree.XMLParser(remove_blank_text=True)
        xml_etree = etree.fromstring(inputxml, parser)

        result = self.conv.extract_copyright_statement('', xml_etree)

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            "<declaration>Tous droits réservés © Approches inductives , 2014</declaration>"
        )

    def test_permissions_copyright_statement_2(self):

        inputxml = """
            <admin>
                <droitsauteur>Tous droits réservés © <nomorg>Approches inductives</nomorg>, 2014</droitsauteur>
            </admin>"""

        parser = etree.XMLParser(remove_blank_text=True)
        xml_etree = etree.fromstring(inputxml, parser)

        result = self.conv.extract_copyright_statement('', xml_etree)

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            "<declaration>Tous droits réservés © Approches inductives , 2014</declaration>"
        )

    def test_permissions_copyright_statement_3(self):

        inputxml = """
            <admin>
                <droitsauteur>
                    <declaration>Tous droits réservés ©</declaration>
                    <annee>2014</annee>
                    <nomorg>Approches inductives</nomorg>
                </droitsauteur>
            </admin>"""

        parser = etree.XMLParser(remove_blank_text=True)
        xml_etree = etree.fromstring(inputxml, parser)

        result = self.conv.extract_copyright_statement('', xml_etree)

        self.assertEqual(
            etree.tostring(result, encoding="utf-8").decode('utf-8'),
            "<declaration>Tous droits réservés © 2014 Approches inductives</declaration>"
        )

    def test_permissions_copyright_holder(self):

        result = self.xml.find("front/article-meta/permissions/copyright-holder").text

        self.assertEqual(result, "Approches inductives")

    def test_permissions_copyright_year(self):

        result = self.xml.find("front/article-meta/permissions/copyright-year").text

        self.assertEqual(result, "2014")

    def test_permissions_copyright_license_link(self):

        result = self.xml.find("front/article-meta/permissions/license").get('{http://www.w3.org/1999/xlink}href')

        self.assertEqual(result, "http://creativecommons.org/licenses/by-sa/3.0/")

    def test_permissions_copyright_license_link_image(self):

        result = self.xml.find("front/article-meta/permissions/license/license-p/graphic").get('{http://www.w3.org/1999/xlink}href')

        self.assertEqual(result, "http://i.creativecommons.org/l/by-sa/3.0/88x31.png")

    def test_abstract_with_lists(self):
        inputxml = """
            <article lang="fr">
                <liminaire>
                    <resume typeresume="resume" lang="fr">
                        <alinea>Contrairement à d’autres crimes commis au sein du cercle familial, le crime passionnel, pourtant très visible socialement, n’a jamais fait l’objet d’une critique sociale ou psychologique efficace comme c’est le cas pour l’infanticide depuis longtemps déjà, ou plus récemment pour les abus sexuels ou le viol conjugal.</alinea>
                        <alinea>Sur la base d’un corpus de 337 crimes et d’outils d’analyse variés, nous soulignerons trois aspects:</alinea>
                        <listenonord signe="tiret">
                            <elemliste>
                                <alinea>Dangerosité du milieu familial et conjugal, surtout pour les femmes.</alinea>
                            </elemliste>
                            <elemliste>
                                <alinea>Déni de cette dangerosité dans le discours médiatique, voire psychiatrique.</alinea>
                            </elemliste>
                            <elemliste>
                                <alinea>Dangerosité masquée enfin, car ces criminels, hommes et femmes, fonctionnent dans une pseudo-normalité.</alinea>
                            </elemliste>
                        </listenonord>
                    </resume>
                </liminaire>
            </article>
        """

        conv = converters.EruditArticle2EruditPS(io.BytesIO(inputxml.encode('utf-8')))
        self.xml = conv.transform(lxml_etree=True, remove_namespace=True)

        result = self.xml.find("front/article-meta/abstract[@{http://www.w3.org/XML/1998/namespace}lang='fr']")

        expected = """
            <abstract xml:lang="fr">
                <p>Contrairement à d’autres crimes commis au sein du cercle familial, le crime passionnel, pourtant très visible socialement, n’a jamais fait l’objet d’une critique sociale ou psychologique efficace comme c’est le cas pour l’infanticide depuis longtemps déjà, ou plus récemment pour les abus sexuels ou le viol conjugal.</p>
                <p>Sur la base d’un corpus de 337 crimes et d’outils d’analyse variés, nous soulignerons trois aspects:</p>
                <list list-type="simple">
                    <list-item><p>Dangerosité du milieu familial et conjugal, surtout pour les femmes.</p></list-item>
                    <list-item><p>Déni de cette dangerosité dans le discours médiatique, voire psychiatrique.</p></list-item>
                    <list-item><p>Dangerosité masquée enfin, car ces criminels, hommes et femmes, fonctionnent dans une pseudo-normalité.</p></list-item>
                </list>
            </abstract>
        """

        """
            <abstract xml:lang="fr">
                <p>Contrairement à d’autres crimes commis au sein du cercle familial, le crime passionnel, pourtant très visible socialement, n’a jamais fait l’objet d’une critique sociale ou psychologique efficace comme c’est le cas pour l’infanticide depuis longtemps déjà, ou plus récemment pour les abus sexuels ou le viol conjugal.</p><p>Sur la base d’un corpus de 337 crimes et d’outils d’analyse variés, nous soulignerons trois aspects:</p>
                <list list-type="simple">
                    <list-item><p><p>Dangerosité du milieu familial et conjugal, surtout pour les femmes.</p></p></list-item><list-item><p><p>Déni de cette dangerosité dans le discours médiatique, voire psychiatrique.</p></p></list-item><list-item><p><p>Dangerosité masquée enfin, car ces criminels, hommes et femmes, fonctionnent dans une pseudo-normalité.</p></p></list-item></list></abstract>
        """
        self.maxDiff = None
        parser = etree.XMLParser(remove_blank_text=True)
        self.assertEqual(
            etree.tostring(result),
            etree.tostring(etree.fromstring(expected, parser))
        )

    def test_abstract(self):

        result = self.xml.find("front/article-meta/abstract[@{http://www.w3.org/XML/1998/namespace}lang='fr']")

        expected = """
            <abstract xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="fr">
                <title>Resume</title>
                <p>Le but de cet article est de présenter les raisons du choix d’une approche inductive, plutôt qu’une approche déductive, afin d’étudier la musique rock chrétienne. Cette étude dresse un portrait des chansons les plus populaires de la musique rock chrétienne tout en décrivant quantitativement les éléments structurels de ces dernières. Afin de réaliser ce projet, nous avons répertorié tous les numéros un du palmarès américain <italic>Christian Songs</italic> depuis sa création en 2003\xa0jusqu’à la fin de l’année 2011, soit 65\xa0chansons. Le portrait de la musique rock chrétienne se décline en onze catégories dont les plus récurrentes sont la dévotion, la présence de Dieu et l’espoir. Cette musique est aussi chantée majoritairement par des hommes et se caractérise par un rythme lent.</p>
            </abstract>
        """

        parser = etree.XMLParser(remove_blank_text=True)
        self.maxDiff = None
        self.assertEqual(
            etree.tostring(result),
            etree.tostring(etree.fromstring(expected, parser))
        )

    def test_trans_abstract(self):

        result = self.xml.find("front/article-meta/trans-abstract[@{http://www.w3.org/XML/1998/namespace}lang='en']")

        expected = """
            <trans-abstract xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="en">
                <title>Abstract</title>
                <p>Abstract translation sample.</p>
            </trans-abstract>
        """

        parser = etree.XMLParser(remove_blank_text=True)
        self.maxDiff = None
        self.assertEqual(
            etree.tostring(result),
            etree.tostring(etree.fromstring(expected, parser))
        )

    def test_keywords(self):

        result = self.xml.findall("front/article-meta/kwd-group[@{http://www.w3.org/XML/1998/namespace}lang='fr']/kwd")

        result = ';'.join([i.text for i in result])

        expected = "Étude mixte;méthodologie inductive;musique rock chrétienne;analyse de contenu"

        self.assertEqual(result, expected)

    def test_ref_count(self):

        result = self.xml.find("front/article-meta/counts/ref-count").get('count')

        self.assertEqual(result, '61')

    def test_table_count(self):

        result = self.xml.find("front/article-meta/counts/table-count").get('count')

        self.assertEqual(result, '6')

    def test_fig_count(self):

        result = self.xml.find("front/article-meta/counts/fig-count").get('count')

        self.assertEqual(result, '3')

    def test_equation_count(self):

        result = self.xml.find("front/article-meta/counts/equation-count").get('count')

        self.assertEqual(result, '3')

    def test_page_count_ppage_absent(self):
        pagination = self.conv.source_etree.find("admin/infoarticle/pagination")
        ppage = pagination.find('ppage')
        pagination.remove(ppage)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_dpage_absent(self):
        pagination = self.conv.source_etree.find("admin/infoarticle/pagination")
        dpage = pagination.find('dpage')
        pagination.remove(dpage)

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_ppage_bigger_dpage_absent(self):
        ppage = self.conv.source_etree.find("admin/infoarticle/pagination/ppage")
        dpage = self.conv.source_etree.find("admin/infoarticle/pagination/dpage")
        ppage.text = '120'
        dpage.text = '100'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_ppage_not_number(self):
        ppage = self.conv.source_etree.find("admin/infoarticle/pagination/ppage")
        ppage.text = 'a'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_page_count_dpage_not_number(self):
        dpage = self.conv.source_etree.find("admin/infoarticle/pagination/dpage")
        dpage.text = 'a'

        custom_xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

        result = custom_xml.find("front/article-meta/counts/page-count")

        self.assertEqual(result, None)

    def test_paragraph_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='paragraph']").get('count')

        self.assertEqual(result, '32')

    def test_notes_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='note']").get('count')

        self.assertEqual(result, '6')

    def test_words_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='word']").get('count')

        self.assertEqual(result, '4951')

    def test_videos_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='video']").get('count')

        self.assertEqual(result, '0')

    def test_audios_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='audio']").get('count')

        self.assertEqual(result, '0')

    def test_media_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='media']").get('count')

        self.assertEqual(result, '8')

    def test_image_count(self):

        result = self.xml.find("front/article-meta/counts/count[@count-type='image']").get('count')

        self.assertEqual(result, '8')

    def test_ack(self):

        result = self.xml.find("back/ack")

        self.assertEqual(result.find('title').text, 'Merci')

        expected = b"""<ack xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><title>Merci</title><p>Cet <italic>article</italic> est une version modifi&#233;e d&#8217;un texte pr&#233;sent&#233; au s&#233;minaire HPES du CLERSE (Universit&#233; Lille I). Nous remercions Vincent Duwicquet, Jordan Melmi&#232;s et Jonathan Marie pour leurs commentaires, Malika Riboudt pour l&#8217;assistance technique sur Maple, Marc Lavoie et Louis-Philippe Rochon pour leurs conseils. Nous tenons &#233;galement &#224; faire part de notre gratitude aux rapporteurs de la revue pour leurs remarques pertinentes. N&#233;anmoins, nous demeurons seuls responsables des erreurs pouvant subsister.</p></ack>"""

        self.assertEqual(etree.tostring(result), expected)

    def test_xref_fn(self):

        result = ['-'.join([i.get('ref-type'), i.get('rid'), i.text]) for i in self.xml.findall("body//xref[@ref-type='fn']")]

        expected = ['fn-no1-1', 'fn-no2-2', 'fn-no3-3', 'fn-no4-4', 'fn-no5-5', 'fn-no6-6']

        self.assertEqual(result, expected)

    def test_table_wrap_label(self):

        result = self.xml.find("body//table-wrap[@id='ta1']")

        self.assertEqual(result.find('label').text.strip(), 'Tableau 1')

    def test_table_wrap_caption(self):

        result = self.xml.find("body//table-wrap[@id='ta1']")

        self.assertEqual(result.find('caption/title').text.strip(), 'Synthèse des analyses de contenu aux États-Unis, 1969-2006')

    def test_table_wrap_notes(self):

        result = self.xml.find("body//table-wrap[@id='ta1']/table-wrap-foot/fn-group/fn[@id='tnt1']/p").text.strip()

        self.assertEqual(result, 'Sample of table notes')

    def test_table_wrap_with_text_table(self):

        result = self.xml.find("body//table-wrap[@id='ta6']")

        expected = b'<table-wrap xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" id="ta6"><label>Tableau 4</label><caption xml:lang="fr"><title>Statistiques des &#233;difices et de leur destruction &#224; Lamaria</title></caption><table><colgroup><col align="left" valign="middle"/><col align="center"/><col align="center"/><col align="center"/></colgroup><thead><tr><th align="center" valign="middle">Maisons</th><th align="center">Secteur urbain</th><th align="center">Secteur rural</th><th align="center">Total</th></tr></thead><tfoot><tr><td align="right" valign="middle">Total</td><td align="right">4834</td><td align="right">2686</td><td align="right">7520</td></tr></tfoot><tbody><tr><td align="left" valign="middle">D&#233;truites</td><td align="center">1888</td><td align="center">1198</td><td align="center">3086</td></tr><tr><td align="left" valign="middle">Endommag&#233;es</td><td align="center">1342</td><td align="center">297</td><td align="center">1639</td></tr><tr><td align="left" valign="middle">Sous-total</td><td align="center">3230</td><td align="center">1495</td><td align="center">4725</td></tr><tr><td align="left" valign="middle">Intactes</td><td align="center">1604</td><td align="center">1191</td><td align="center">2795</td></tr></tbody></table></table-wrap>'

        self.maxDiff = None

        self.assertSequenceEqual(etree.tostring(result), expected)

    def test_table_wrap_attrib(self):

        result = self.xml.find("body//table-wrap[@id='ta1']/table-wrap-foot/attrib").text.strip()

        self.assertEqual(result, 'Sample of source data')

    def test_table_wrap_graphic(self):

        result = self.xml.find("body//table-wrap[@id='ta1']/graphic")

        self.assertEqual(result.get('position').strip(), 'float')

        self.assertEqual(result.get('content-type').strip(), 'table')

        self.assertEqual(result.get('{http://www.w3.org/1999/xlink}href').strip(), 'image_tableau_1.png')

    def test_figure_label(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('label').text.strip(), 'Figure 1')

    def test_figure_caption(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('caption/title').text.strip(), 'Modèle des valeurs de Schwartz (1992)')

    def test_figure_alt_text(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('alt-text').text.strip(), 'Sample of figure notes')

    def test_figure_attrib(self):

        result = self.xml.find("body//fig[@id='fi1']")

        self.assertEqual(result.find('attrib').text.strip(), 'Sample of source data')

    def test_fig_graphic(self):

        result = self.xml.find("body//fig[@id='fi1']/graphic")

        self.assertEqual(result.get('position').strip(), 'float')

        self.assertEqual(result.get('content-type').strip(), 'figure')

        self.assertEqual(result.get('{http://www.w3.org/1999/xlink}href').strip(), 'image_figure_1.png')
