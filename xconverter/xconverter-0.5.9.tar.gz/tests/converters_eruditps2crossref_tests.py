import unittest
import os

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