"""JSON-schema action contract for constrained local generation."""
def obj(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}

ARGUMENTS={
    'schema':obj({}), 'document':obj({}), 'quality':obj({}), 'compare':obj({}),
    'sql':obj({'query':{'type':'string','maxLength':4000}}),
    'scenario':obj({'segment':{'type':'string','enum':['small','large']},
                    'lift':{'type':'number','minimum':0,'maximum':.2},
                    'cost':{'type':'number','minimum':0,'maximum':10000}}),
    'finish':obj({'decision':{'type':'string','enum':['hold','pilot']},
                  'evidence_ids':{'type':'array','items':{'type':'string'},'maxItems':12}})
}
ACTION_SCHEMA={'anyOf':[obj({'tool':{'type':'string','enum':[name]},'args':args}) for name,args in ARGUMENTS.items()]}
