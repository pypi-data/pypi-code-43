from unittest import TestCase

from sekg.text.util import CodeTextPreprocessor


class TestCodeTextPreprocessor(TestCase):
    def test_clean_html_text(self):
        html_text = """
<div class="block"><p>
 The <tt>Marshaller</tt> class is responsible for governing the process
 of serializing Java content trees back into XML data.  It provides the basic
 marshalling methods:

 </p><p>
 <i>Assume the following setup code for all following code fragments:</i>
 </p><blockquote>
    <pre>       JAXBContext jc = JAXBContext.newInstance( "com.acme.foo" );
       Unmarshaller u = jc.createUnmarshaller();
       Object element = u.unmarshal( new File( "foo.xml" ) );
       Marshaller m = jc.createMarshaller();
    </pre>
 </blockquote>

 <p>
 Marshalling to a File:
 </p><blockquote>
    <pre>       OutputStream os = new FileOutputStream( "nosferatu.xml" );
       m.marshal( element, os );
    </pre>
 </blockquote>

 <p>
 Marshalling to a SAX ContentHandler:
 </p><blockquote>
    <pre>       // assume MyContentHandler instanceof ContentHandler
       m.marshal( element, new MyContentHandler() );
    </pre>
 </blockquote>

 <p>
 Marshalling to a DOM Node:
 </p><blockquote>
    <pre>       DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
       dbf.setNamespaceAware(true);
       DocumentBuilder db = dbf.newDocumentBuilder();
       Document doc = db.newDocument();

       m.marshal( element, doc );
    </pre>
 </blockquote>

 <p>
 Marshalling to a java.io.OutputStream:
 </p><blockquote>
    <pre>       m.marshal( element, System.out );
    </pre>
 </blockquote>

 <p>
 Marshalling to a java.io.Writer:
 </p><blockquote>
    <pre>       m.marshal( element, new PrintWriter( System.out ) );
    </pre>
 </blockquote>

 <p>
 Marshalling to a javax.xml.transform.SAXResult:
 </p><blockquote>
    <pre>       // assume MyContentHandler instanceof ContentHandler
       SAXResult result = new SAXResult( new MyContentHandler() );

       m.marshal( element, result );
    </pre>
 </blockquote>

 <p>
 Marshalling to a javax.xml.transform.DOMResult:
 </p><blockquote>
    <pre>       DOMResult result = new DOMResult();

       m.marshal( element, result );
    </pre>
 </blockquote>

 <p>
 Marshalling to a javax.xml.transform.StreamResult:
 </p><blockquote>
    <pre>       StreamResult result = new StreamResult( System.out );

       m.marshal( element, result );
    </pre>
 </blockquote>

 <p>
 Marshalling to a javax.xml.stream.XMLStreamWriter:
 </p><blockquote>
    <pre>       XMLStreamWriter xmlStreamWriter =
           XMLOutputFactory.newInstance().createXMLStreamWriter( ... );

       m.marshal( element, xmlStreamWriter );
    </pre>
 </blockquote>

 <p>
 Marshalling to a javax.xml.stream.XMLEventWriter:
 </p><blockquote>
    <pre>       XMLEventWriter xmlEventWriter =
           XMLOutputFactory.newInstance().createXMLEventWriter( ... );

       m.marshal( element, xmlEventWriter );
    </pre>
 </blockquote>

 <p>
 <a name="elementMarshalling"></a>
 <b>Marshalling content tree rooted by a JAXB element</b><br>
 </p><blockquote>
 The first parameter of the overloaded
 <tt>Marshaller.marshal(java.lang.Object, ...)</tt> methods must be a
 JAXB element as computed by
 <a href="../../../javax/xml/bind/JAXBIntrospector.html#isElement(java.lang.Object)"><code>JAXBIntrospector.isElement(java.lang.Object)</code></a>;
 otherwise, a <tt>Marshaller.marshal</tt> method must throw a
 <a href="../../../javax/xml/bind/MarshalException.html" title="class in javax.xml.bind"><code>MarshalException</code></a>. There exist two mechanisms
 to enable marshalling an instance that is not a JAXB element.
 One method is to wrap the instance as a value of a <a href="../../../javax/xml/bind/JAXBElement.html" title="class in javax.xml.bind"><code>JAXBElement</code></a>,
 and pass the wrapper element as the first parameter to
 a <tt>Marshaller.marshal</tt> method. For java to schema binding, it
 is also possible to simply annotate the instance's class with
 @<a href="../../../javax/xml/bind/annotation/XmlRootElement.html" title="annotation in javax.xml.bind.annotation"><code>XmlRootElement</code></a>.
 </blockquote>

 <p>
 <b>Encoding</b><br>
 </p><blockquote>
 By default, the Marshaller will use UTF-8 encoding when generating XML data
 to a <tt>java.io.OutputStream</tt>, or a <tt>java.io.Writer</tt>.  Use the
 <a href="../../../javax/xml/bind/Marshaller.html#setProperty(java.lang.String,%20java.lang.Object)"><code>setProperty</code></a> API to change the output
 encoding used during these marshal operations.  Client applications are
 expected to supply a valid character encoding name as defined in the
 <a href="http://www.w3.org/TR/2000/REC-xml-20001006#charencoding">W3C XML 1.0
 Recommendation</a> and supported by your
 <a href="http://java.sun.com/j2se/1.3/docs/api/java/lang/package-summary.html#charenc">
 Java Platform</a>.
 </blockquote>

 <p>
 <b>Validation and Well-Formedness</b><br>
 </p><blockquote>
 <p>
 Client applications are not required to validate the Java content tree prior
 to calling any of the marshal API's.  Furthermore, there is no requirement
 that the Java content tree be valid with respect to its original schema in
 order to marshal it back into XML data.  Different JAXB Providers will
 support marshalling invalid Java content trees at varying levels, however
 all JAXB Providers must be able to marshal a valid content tree back to
 XML data.  A JAXB Provider must throw a <tt>MarshalException</tt> when it
 is unable to complete the marshal operation due to invalid content.  Some
 JAXB Providers will fully allow marshalling invalid content, others will fail
 on the first validation error.
 </p><p>
 Even when schema validation is not explictly enabled for the marshal operation,
 it is possible that certain types of validation events will be detected
 during the operation.  Validation events will be reported to the registered
 event handler.  If the client application has not registered an event handler
 prior to invoking one of the marshal API's, then events will be delivered to
 a default event handler which will terminate the marshal operation after
 encountering the first error or fatal error. Note that for JAXB 2.0 and
 later versions, <a href="../../../javax/xml/bind/helpers/DefaultValidationEventHandler.html" title="class in javax.xml.bind.helpers"><code>DefaultValidationEventHandler</code></a> is
 no longer used.

 </p></blockquote>

 <p>
 <a name="supportedProps"></a>
 <b>Supported Properties</b><br>
 </p><blockquote>
 <p>
 All JAXB Providers are required to support the following set of properties.
 Some providers may support additional properties.
 </p><dl>
   <dt><tt>jaxb.encoding</tt> - value must be a java.lang.String</dt>
   <dd>The output encoding to use when marshalling the XML data.  The
               Marshaller will use "UTF-8" by default if this property is not
       specified.</dd>
   <dt><tt>jaxb.formatted.output</tt> - value must be a java.lang.Boolean</dt>
   <dd>This property controls whether or not the Marshaller will format
       the resulting XML data with line breaks and indentation.  A
       true value for this property indicates human readable indented
       xml data, while a false value indicates unformatted xml data.
       The Marshaller will default to false (unformatted) if this
       property is not specified.</dd>
   <dt><tt>jaxb.schemaLocation</tt> - value must be a java.lang.String</dt>
   <dd>This property allows the client application to specify an
       xsi:schemaLocation attribute in the generated XML data.  The format of
       the schemaLocation attribute value is discussed in an easy to
       understand, non-normative form in
       <a href="http://www.w3.org/TR/xmlschema-0/#schemaLocation">Section 5.6
       of the W3C XML Schema Part 0: Primer</a> and specified in
       <a href="http://www.w3.org/TR/xmlschema-1/#Instance_Document_Constructions">
       Section 2.6 of the W3C XML Schema Part 1: Structures</a>.</dd>
   <dt><tt>jaxb.noNamespaceSchemaLocation</tt> - value must be a java.lang.String</dt>
   <dd>This property allows the client application to specify an
       xsi:noNamespaceSchemaLocation attribute in the generated XML
       data.  The format of the schemaLocation attribute value is discussed in
       an easy to understand, non-normative form in
       <a href="http://www.w3.org/TR/xmlschema-0/#schemaLocation">Section 5.6
       of the W3C XML Schema Part 0: Primer</a> and specified in
       <a href="http://www.w3.org/TR/xmlschema-1/#Instance_Document_Constructions">
       Section 2.6 of the W3C XML Schema Part 1: Structures</a>.</dd>
   <dt><tt>jaxb.fragment</tt> - value must be a java.lang.Boolean</dt>
   <dd>This property determines whether or not document level events will be
       generated by the Marshaller.  If the property is not specified, the
       default is <tt>false</tt>. This property has different implications depending
       on which marshal api you are using - when this property is set to true:<br>
       <ul>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20org.xml.sax.ContentHandler)"><code>marshal(Object,ContentHandler)</code></a> - the Marshaller won't
             invoke <a href="../../../org/xml/sax/ContentHandler.html#startDocument()"><code>ContentHandler.startDocument()</code></a> and
             <a href="../../../org/xml/sax/ContentHandler.html#endDocument()"><code>ContentHandler.endDocument()</code></a>.</li>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20org.w3c.dom.Node)"><code>marshal(Object,Node)</code></a> - the property has no effect on this
             API.</li>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20java.io.OutputStream)"><code>marshal(Object,OutputStream)</code></a> - the Marshaller won't
             generate an xml declaration.</li>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20java.io.Writer)"><code>marshal(Object,Writer)</code></a> - the Marshaller won't
             generate an xml declaration.</li>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20javax.xml.transform.Result)"><code>marshal(Object,Result)</code></a> - depends on the kind of
             Result object, see semantics for Node, ContentHandler, and Stream APIs</li>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20javax.xml.stream.XMLEventWriter)"><code>marshal(Object,XMLEventWriter)</code></a> - the
             Marshaller will not generate <a href="../../../javax/xml/stream/XMLStreamConstants.html#START_DOCUMENT"><code>XMLStreamConstants.START_DOCUMENT</code></a> and
             <a href="../../../javax/xml/stream/XMLStreamConstants.html#END_DOCUMENT"><code>XMLStreamConstants.END_DOCUMENT</code></a> events.</li>
         <li><a href="../../../javax/xml/bind/Marshaller.html#marshal(java.lang.Object,%20javax.xml.stream.XMLStreamWriter)"><code>marshal(Object,XMLStreamWriter)</code></a> - the
             Marshaller will not generate <a href="../../../javax/xml/stream/XMLStreamConstants.html#START_DOCUMENT"><code>XMLStreamConstants.START_DOCUMENT</code></a> and
             <a href="../../../javax/xml/stream/XMLStreamConstants.html#END_DOCUMENT"><code>XMLStreamConstants.END_DOCUMENT</code></a> events.</li>
       </ul>
   </dd>
 </dl>
 </blockquote>

 <p>
 <a name="marshalEventCallback"></a>
 <b>Marshal Event Callbacks</b><br>
 </p><blockquote>
 "The <a href="../../../javax/xml/bind/Marshaller.html" title="interface in javax.xml.bind"><code>Marshaller</code></a> provides two styles of callback mechanisms
 that allow application specific processing during key points in the
 unmarshalling process.  In 'class defined' event callbacks, application
 specific code placed in JAXB mapped classes is triggered during
 marshalling.  'External listeners' allow for centralized processing
 of marshal events in one callback method rather than by type event callbacks.

 <p>
 Class defined event callback methods allow any JAXB mapped class to specify
 its own specific callback methods by defining methods with the following method signatures:
 </p><blockquote>
 <pre>   // Invoked by Marshaller after it has created an instance of this object.
   boolean beforeMarshal(Marshaller);

   // Invoked by Marshaller after it has marshalled all properties of this object.
   void afterMmarshal(Marshaller);
 </pre>
 </blockquote>
 The class defined event callback methods should be used when the callback method requires
 access to non-public methods and/or fields of the class.
 <p>
 The external listener callback mechanism enables the registration of a <a href="../../../javax/xml/bind/Marshaller.Listener.html" title="class in javax.xml.bind"><code>Marshaller.Listener</code></a>
 instance with a <a href="../../../javax/xml/bind/Marshaller.html#setListener(javax.xml.bind.Marshaller.Listener)"><code>setListener(Listener)</code></a>. The external listener receives all callback events,
 allowing for more centralized processing than per class defined callback methods.
 </p><p>
 The 'class defined' and external listener event callback methods are independent of each other,
 both can be called for one event. The invocation ordering when both listener callback methods exist is
 defined in <a href="../../../javax/xml/bind/Marshaller.Listener.html#beforeMarshal(java.lang.Object)"><code>Marshaller.Listener.beforeMarshal(Object)</code></a> and <a href="../../../javax/xml/bind/Marshaller.Listener.html#afterMarshal(java.lang.Object)"><code>Marshaller.Listener.afterMarshal(Object)</code></a>.
 </p><p>
 An event callback method throwing an exception terminates the current marshal process.
 </p></blockquote></div>
"""
        preprocessor = CodeTextPreprocessor()
        clean = preprocessor.clean_html_text(html_text=html_text)
        print(clean)
