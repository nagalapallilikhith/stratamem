"""Behavioral checks; fake Hindsight transport never calls a live service."""
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app

class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        app.DATA=Path(self.tmp.name)
        app.initialize()
        self.w=app.rows('SELECT id FROM workspaces')[0]['id']

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self):
        for step in range(3): app.action('/api/demo-step',{'workspace':self.w,'step':step})

    def hyp(self):
        return app.hypothesis({'workspace':self.w,'statement':'ACME may expand into enterprise sales.', 'expected':'Enterprise pricing is launched later.', 'evidence':[e['id'] for e in app.snapshot(self.w)['events']]})

    def test_persistence_and_counts(self):
        self.seed(); app.initialize()
        s=app.snapshot(self.w)
        self.assertEqual(s['counts'],{'events':3,'memories':3,'synced':0,'open':0})
        app.action('/api/demo-step',{'workspace':self.w,'step':0})
        self.assertEqual(app.snapshot(self.w)['counts']['events'],3)

    def test_history_changes_local_answer(self):
        app.action('/api/demo-step',{'workspace':self.w,'step':0})
        early=app.analyze({'workspace':self.w})
        self.seed(); later=app.analyze({'workspace':self.w})
        self.assertNotEqual(early['answer'],later['answer'])
        self.assertEqual(later['title'],'An enterprise expansion is plausible')
        self.assertEqual(later['recalled'],[])

    def test_contradiction_and_lesson_reuse(self):
        self.seed(); hid=self.hyp()
        eid=app.action('/api/demo-outcome',{'workspace':self.w,'reject':True})['id']
        app.evaluate({'id':hid,'status':'REJECTED','event':eid,'note':'Cancellation contradicts expansion; earlier hiring alone was insufficient.'})
        result=app.analyze({'workspace':self.w})
        self.assertEqual(result['title'],'The evidence is mixed')
        self.assertEqual(len(result['lesson_ids']),1)
        self.assertIn('Cancellation',result['lesson_note'])
        with self.assertRaises(ValueError): app.evaluate({'id':hid,'status':'SUPPORTED','event':eid,'note':'No double evaluation permitted.'})

    def test_no_future_leakage(self):
        self.seed(); old=app.workspace(self.w)
        fresh=app.action('/api/demo',{})['id']
        self.assertNotEqual(app.workspace(fresh)['bank'],old['bank'])
        self.assertEqual(app.snapshot(fresh)['events'],[])
        self.assertEqual(app.snapshot(fresh)['lessons'],[])

    def test_no_early_outcome(self):
        self.seed(); hid=self.hyp()
        with self.assertRaisesRegex(ValueError,'after'):
            app.evaluate({'id':hid,'status':'SUPPORTED','event':app.snapshot(self.w)['events'][0]['id'],'note':'An earlier event cannot be a later outcome.'})

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):app.add_event({'workspace':self.w,'title':'short','date':'nope','type':'Hiring'})
        with self.assertRaises(ValueError):app.add_event({'workspace':self.w,'title':'A valid title','date':'2026-01-01','type':'Hiring','source':'javascript:alert(1)'})
        with self.assertRaises(ValueError):app.add_event({'workspace':self.w,'title':'A valid title','date':'2026-01-01','type':'Hiring','synthetic':False})

    def test_hindsight_result_is_displayed_and_counts_real_calls(self):
        self.seed()
        calls=[]
        class Fake:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def create_bank(self,**kw):calls.append('bank')
            def retain(self,**kw):calls.append('retain')
            def recall(self,**kw):calls.append('recall');return types.SimpleNamespace(results=[types.SimpleNamespace(id='fact-1',text='A genuine transport result in this test')])
            def reflect(self,**kw):calls.append('reflect');return types.SimpleNamespace(text='This text came from the mocked Hindsight response, not a canned frontend answer.')
        with patch.object(app,'client',return_value=Fake()):
            a=app.analyze({'workspace':self.w,'engine':'hindsight'})
        self.assertEqual(calls.count('retain'),3)
        self.assertEqual(calls.count('reflect'),1)
        self.assertEqual(a['recalled'][0]['id'],'fact-1')
        self.assertIn('mocked Hindsight response',a['answer'])
        self.assertEqual(app.snapshot(self.w)['counts']['synced'],3)

    def test_hindsight_failure_is_not_silent_fallback(self):
        self.seed()
        with patch.object(app,'client',side_effect=ValueError('Service unreachable')):
            with self.assertRaisesRegex(ValueError,'Service unreachable'):app.analyze({'workspace':self.w,'engine':'hindsight'})
        self.assertEqual(app.snapshot(self.w)['counts']['synced'],0)
        self.assertIsNone(app.snapshot(self.w)['analysis'])

    def test_other_workspace_cannot_supply_evidence(self):
        self.seed()
        other=app.create_workspace('Other',True)
        with self.assertRaises(ValueError):app.hypothesis({'workspace':other,'statement':'A sufficiently long hypothesis','expected':'A later public event','evidence':[app.snapshot(self.w)['events'][0]['id']]})

if __name__=='__main__':unittest.main(verbosity=2)
