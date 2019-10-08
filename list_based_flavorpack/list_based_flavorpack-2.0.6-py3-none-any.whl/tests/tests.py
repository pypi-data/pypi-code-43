import os
import linecache
from django.test import TestCase
from django.core.management import call_command
from django.test.client import RequestFactory
from quartet_templates.models import Template
from serialbox.discovery import get_generator
from serialbox.api import serializers as sb_serializers
from list_based_flavorpack.models import ListBasedRegion, ProcessingParameters
from serialbox import models as sb_models
from quartet_output.models import EndPoint, AuthenticationInfo
from quartet_capture.models import Rule, Step
from quartet_templates.models import Template


class TemplateTest(TestCase):
    '''
    Tests the Template model.
    '''
    def create_template(self, name: str, content: str, description: str):
        return Template.objects.create(name=name, content=content, description=description)

    def test_template_creation(self):
        content = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:bla:bla">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:SpecialXML>
         <SomethingSpecial>{{ something_special }}</SomethingSpecial>
      </urn:SpecialXML>
   </soapenv:Body>
</soapenv:Envelope>
        '''
        template = self.create_template(name="Test Template", content=content, description="A Test Template")
        self.assertTrue(isinstance(template, Template))

    def test_template_rendering(self):
        content = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:bla:bla">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:SpecialXML>
         <SomethingSpecial>{{ something_special }}</SomethingSpecial>
      </urn:SpecialXML>
   </soapenv:Body>
</soapenv:Envelope>
        '''
        template = self.create_template(name="Test Template", content=content, description="A Test Template")
        rendered = template.render(context={"something_special": "Special Value"})
        expected = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:bla:bla">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:SpecialXML>
         <SomethingSpecial>Special Value</SomethingSpecial>
      </urn:SpecialXML>
   </soapenv:Body>
</soapenv:Envelope>
        '''
        self.assertEqual(expected, rendered)


class ListBasedRegionTest(TestCase):
    '''
    Tests the creation of a list-based region.
    '''
    
    def test_list_based_region_creation(self):
        content = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:bla:bla">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:SpecialXML>
         <RequestSize>{{ allocate.size }}</RequestSize>
      </urn:SpecialXML>
   </soapenv:Body>
</soapenv:Envelope>
        '''
        template =  Template.objects.create(name="test template", content=content, description="A test template")
        list_based_region = ListBasedRegion()
        list_based_region.template = template
        list_based_region.processing_class_path = "list_based_flavorpack.processing_classes.third_party_processing.processing.ThirdPartyProcessingClass"
        list_based_region.directory_path = "/tmp"
        list_based_region.number_replenishment_size = 20
        list_based_region.save()
        self.assertEqual("/tmp/" + str(list_based_region.file_id), list_based_region.file_path)


class UUIDPoolTest(TestCase):
    '''
    Tests the Third Party Processing Class along with the UUID generation step.
    '''
    def setUp(self):
        self.test_pool = self.generate_test_pool()
        self.rule = self.generate_step_rule()
        self.template = self.generate_template()
        self.list_based_region = self.generate_region(self.test_pool, self.rule, self.template)

    def tearDown(self):
        try:
            os.remove(self.list_based_region.file_path)
        except:
            # some tests don't use filesystem.
            pass
    
    def generate_test_pool(self):
        # create pool
        test_pool = sb_models.Pool()
        test_pool.readable_name = "Test Pool"
        test_pool.machine_name = "TestPool"
        test_pool.active = True
        test_pool.request_threshold = 1000
        test_pool.save()
        return test_pool
    
    def generate_region(self, test_pool, rule, template):
        # create region with third party processing class.
        list_based_region = ListBasedRegion()
        list_based_region.processing_class_path = "list_based_flavorpack.processing_classes.third_party_processing.processing.ThirdPartyProcessingClass"
        list_based_region.pool = test_pool
        list_based_region.readable_name = "UUID Region"
        list_based_region.machine_name = "UUIDRegion"
        list_based_region.active = True
        list_based_region.order = 1
        list_based_region.rule = rule
        list_based_region.template = template
        list_based_region.number_replenishment_size = 200
        list_based_region.directory_path = "/tmp"
        list_based_region.save()
        return list_based_region
    
    def generate_template(self):
        content = '''<?xml version="1.0" encoding="UTF-8"?>
<NumberRequest>
    <Type>UUID</Type>
    <Size>{{ allocate.size }}</Size>
</NumberRequest>
        '''
        # create template
        template = Template.objects.create(name="UUID Request", content=content, description="Requests a UUID")
        return template
    
    def generate_step_rule(self):
        # Create Rule and Step
        rule = Rule()
        rule.name = "UUID Rule"
        
        rule.description = "Generates UUIDs to a file"
        rule.save()
        step = Step()
        step.name = "UUID Generate Step"
        step.description = "Generates UUIDs to a file"
        step.step_class = "list_based_flavorpack.steps.UUIDRequestStep"
        step.order = 1
        step.rule = rule
        step.save()
        return rule
    
    def generate_allocation(self, size, test_pool, list_based_region):
        generator = get_generator(test_pool.machine_name)
        request_factory = RequestFactory()
        request = request_factory.get("allocate/TestPool/" + str(size))
        response = generator.get_response(request, size, test_pool.machine_name, None)
        serializer = sb_serializers.ResponseSerializer(response)
        return response

    def test_uuid_pool_correct_filepath(self):
        self.assertEqual("/tmp/" + str(self.list_based_region.file_id), self.list_based_region.file_path)
        
    def test_uuid_pool_200_requested(self):
        self.assertEqual("/tmp/" + str(self.list_based_region.file_id), self.list_based_region.file_path)
        # Now request 5 UUIDs, the file should be written with 200 UUIDs
        size = 5
        response = self.generate_allocation(size, self.test_pool, self.list_based_region)
        # check that there are 200 items written in the file (number replenishment size)
        file_size = sum((1 for i in open(self.list_based_region.file_path)))
        self.assertEqual(200, file_size)
   
    def test_uuid_pool_correct_numbers_returned(self):
        response = self.generate_allocation(5, self.test_pool, self.list_based_region)
        numbers_returned = response.number_list
        # check first five items requested.
        with open(self.list_based_region.file_path, 'r') as f:
            count = 0
            for line in f.readlines():
                self.assertEqual(numbers_returned[count], line.strip())
                count += 1
                if count == 5:
                    break

    def test_uuid_pool_correct_numbers_returned_2_calls(self):
        linecache.checkcache(filename=self.list_based_region.file_path)
        response = self.generate_allocation(5, self.test_pool, self.list_based_region)
        numbers_returned = response.number_list
        # check first five items requested.
        max_line = self.list_based_region.last_number_line + 5
        count = 0
        count = 0
        for lineno in range(1, 5):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1
        response = self.generate_allocation(10, self.test_pool, self.list_based_region)
        numbers_returned = response.number_list
        count = 0
        for lineno in range(6, 14):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1

    def test_uuid_pool_correct_numbers_returned_5_calls_replenish_once(self):
        all_numbers_returned = []
        linecache.checkcache(filename=self.list_based_region.file_path)
        response = self.generate_allocation(5, self.test_pool, self.list_based_region)
        # with a request of 5, we should have 200 items in the file.
        file_size = sum((1 for i in open(self.list_based_region.file_path)))
        self.assertEqual(200, file_size)
        numbers_returned = response.number_list
        all_numbers_returned += response.number_list
        # check first five items requested.
        count = 0
        for lineno in range(1, 6):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1
        response = self.generate_allocation(10, self.test_pool, self.list_based_region)

        # with another request of 10, we should still have 200 in the file.
        file_size = sum((1 for i in open(self.list_based_region.file_path)))
        self.assertEqual(200, file_size)        
        numbers_returned = response.number_list
        all_numbers_returned += response.number_list
        count = 0
        linecache.checkcache(filename=self.list_based_region.file_path)        
        for lineno in range(6, 16):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1
        response = self.generate_allocation(100, self.test_pool, self.list_based_region)
        # with another request of 100, we should still just have 200 in the file.        
        file_size = sum((1 for i in open(self.list_based_region.file_path)))
        self.assertEqual(200, file_size)        
        numbers_returned = response.number_list
        all_numbers_returned += response.number_list
        count = 0
        linecache.checkcache(filename=self.list_based_region.file_path)        
        for lineno in range(16, 101):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1
        # replenish now. Next file size should be 400.
        response = self.generate_allocation(150, self.test_pool, self.list_based_region)
        numbers_returned = response.number_list
        all_numbers_returned += response.number_list
        count = 0
        '''
        print(numbers_returned)
        with open(self.list_based_region.file_path, 'r') as f:
            for line in f.readlines():
                count += 1
                print("count: %s" % str(count))
                print(line)
        '''
        count = 0
        # Replenishment should have been triggered and the file should have 400 UUIDs.
        file_size = sum((1 for i in open(self.list_based_region.file_path)))
        self.assertEqual(400, file_size)
        linecache.checkcache(filename=self.list_based_region.file_path)        
        for lineno in range(116, 266):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1

        response = self.generate_allocation(50, self.test_pool, self.list_based_region)
        numbers_returned = response.number_list
        all_numbers_returned += response.number_list
        count = 0
        '''
        print(numbers_returned)
        with open(self.list_based_region.file_path, 'r') as f:
            for line in f.readlines():
                count += 1
                print("count: %s" % str(count))
                print(line)
        '''
        count = 0
        # with another request of 50, we should still have 400 UUIDs in the file.
        file_size = sum((1 for i in open(self.list_based_region.file_path)))
        self.assertEqual(400, file_size)
        linecache.checkcache(filename=self.list_based_region.file_path)        
        for lineno in range(266, 316):
            self.assertEqual(numbers_returned[count], linecache.getline(self.list_based_region.file_path, lineno).strip())
            count += 1

        # Finally overall check the continuity of numbers returned vs numbers in the file.
        # make a list of the 315 items in the file.
        file_numbers_returned = []
        for lineno in range(1, 316):
            file_numbers_returned.append(linecache.getline(self.list_based_region.file_path, lineno).strip())
        self.assertEqual(len(all_numbers_returned), len(file_numbers_returned))
        for i in range(len(file_numbers_returned)):
            self.assertEqual(all_numbers_returned[i], file_numbers_returned[i])
