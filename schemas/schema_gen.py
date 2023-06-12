import json
import re


def main():
    core = bootstrapper()
    core['xTables'] = {}
    schemas = core.keys()
    for schema in schemas:
        xsch = core.get(schema)
        xref = field_refs(xsch)
        core['xTables'][schema] = xref

    schemas = [
        'xEnumerations',
        'xCallables',
        'xIAM',
        'xWorkflows',
        'xSchemas',
        'xRepos',
        'xBOW',
    ]
    schemas = ['xBOW']
    for schema in schemas:
        xref = core['xTables'][schema]
        sch = mini_spec(xref, core)
        #dumper(sch)
        normalized = []
        count = 1
        for fld in sorted(sch, key=lambda x: x.get('sort_order') or 0):
            if (fld.get('collapsed') or fld.get('rows', 0) == 1) and fld.get('fields'):
                for nested in fld['fields']:
                    nested['sort_order'] = count
                    normalized.append(nested)
                    count += 1
            else:
                fld['sort_order'] = count
                normalized.append(fld)
                count += 1
        dumper(normalized)
        #input('Press any key to continue')


def field_refs(schema):
    fields = []
    order = 1
    for fld in schema:
        xref = {'header': fld, 'type': 'TEXT', 'sort_order': order}
        if isinstance(fld, tuple):
            assert len(fld) >= 2, 'Tuple is not constructed right'
            xref['header'] = fld[0]
            xref['type'] = fld[1]
            if len(fld) >= 3:
                xref |= {k.lower(): v for k, v in fld[2].items()}
            if xref['type'] == 'GRID' and xref['xpath'] != 'xApprovals':
                xref['approvals']=False
        if xref['type'] != 'UNSUPPORTED':
            xref['sort_order'] = order
            fields.append(xref)
            order += 1
    return fields


def dumper(ref):
    print(json.dumps(ref, indent=2))


def mini_spec(fields, core):
    specs = []
    for xref in fields:
        fn = core['xMappers'][xref['type']]
        dref = {}
        dref |= xref
        if spec := fn(xref, core):
            dref.update(spec)
            specs.append(dref)
    return specs


def mini_enum(fld, _):
    if fld.get('path'):
        fld['label'] = 'Acronym, Description'
        fld['value'] = 'Acronym'
    if fld.get('xpath'):
        assert False, "XPATH for Enumeration for {fld['header']} not supported"
        # TODO, Make a call to repo and get right columns using field COLUMNS dynamically REPO Registered
        # fld['label'] = 'Column1 , Column2'
        # fld['value'] = 'Column1'
    return fld


def mini_text(fld, _):
    return fld


def mini_grid(fld, core):
    xpath = fld.get('grid')
    if pth := fld.get('xpath'):
        print(f'Generating nested  on reference of other table {pth}')
        xpath = core['xTables'].get(pth)
        assert xpath, f'Nested specfication {pth} not provided'
    assert xpath, 'Grid or Nested specfication not provided'
    flds = mini_spec(xpath, core)
    #[i for i in [mini_spec(k, core) for k in xpath] if i]
    if not fld.get('approval'):
        flds = [i for i in flds if i['header'] != 'Approvals']
        for xref in flds:
            xref['parent'] = fld['header']
    return {'header': fld['header'], 'fields': flds}


def mini_numeric(fld, _):
    return fld


def mini_switch(fld, _):
    return fld


def mini_uri(fld, _):
    return fld


def uri_validator(uri):
    protocols=['http', 'https', 'txform', 'qzt', 'csv', 'xls', 'file']
    sep='://'
    has_protocol=re.search(sep, uri)
    assert has_protocol, f'Protocol not seen in URI {uri}'
    protocol, uri=uri.split(sep)
    assert protocol in protocols, f'Unsupported Protocol {protocol} URI {uri}'
    return True


def bootstrapper():
    return {
        'xApprovals': [
            'Approver',
            ('Order', 'NUMERIC'),
            ('Go Ahead', 'ENUM', {'PATH': '/CORE/APPROVALS/STATUS'}),
            'Remarks',
        ],
        'xEnumerations': [
            ('Domain', 'TEXT', {'LENGTH': 10}),
            ('Entity', 'TEXT', {'LENGTH': 10}),
            ('Acronym', 'TEXT', {'LENGTH': 8}),
            'Description',
            ('Provider', 'URI'),
            'Usage',
            ('Approvals', 'GRID', {'XPATH': 'xApprovals', 'ROWS': 1}),
            ('Validators', 'GRID', {'XPATH': 'xCallables'}),
        ],
        'xRepos': [
            'Repository',
            ('Protocol', 'ENUM', {'PATH': '/CORE/INFRA/PROTOCOLS'}),
            ('Data Store', 'URI'),
            'Description',
            ('Approvals', 'GRID', {'XPATH': 'xApprovals', 'ROWS': 1}),
            ('Validators', 'GRID', {'XPATH': 'xCallables'}),
        ],
        'xIAM': [
            ('Role', 'ENUM', {'PATH': '/CORE/IAM/ROLES'}),
            ('Entity', 'ENUM', {'PATH': '/CORE/IAM/ENTITY'}),
            'Who',
            ('Approvals', 'GRID', {'XPATH': 'xApprovals'}),
            ('Validators', 'GRID', {'XPATH': 'xCallables'}),
        ],
        'xParameters': [
            'Parameter',
            ('Type', 'ENUM', {'PATH': '/CORE/REGISTRY/DATA TYPES'}),
            ('Operator', 'ENUM', {'PATH': '/CORE/REGISTRY/OPERATORS'}),
            'Value',
        ],
        'xCallables': [
            'Callable',
            ('Post Fix Params', 'GRID', {'XPATH': 'xParameters'}),
            ('Approvals', 'GRID', {'XPATH': 'xApprovals'}),
        ],
        'xWorkflows': [
            'Workflow',
            ('Order', 'NUMERIC'),
            ('Approvals', 'GRID', {'XPATH': 'xApprovals'}),
            ('Side Effects', 'GRID', {'XPATH': 'xCallables'}),
        ],
        'xFields': [
            'Column',
            ('Order', 'NUMERIC'),
            ('Is Key', 'SWITCH'),
            'Description',
            ('Type', 'ENUM', {'PATH': 'CORE/REGISTRY/DATA TYPES'}),
            'Default',
            'Grid',
            ('Length', 'NUMERIC'),
            ('Rows', 'NUMERIC'),
            ('URI', 'URI'),
            'Enum Source',
            'Enum Label',
            'Enum Value',
            ('Is Hidden', 'SWITCH'),
            ('Is Read Only', 'SWITCH'),
            ('Is Nullable', 'SWITCH'),
            'DB Field',
            ('Validators', 'GRID', {'XPATH': 'xCallables'}),
        ],
        'xSchemas': [
            'xSchema',
            'Path',
            ('Fields', 'GRID', {'XPATH': 'xFields'}),
            ('IAM', 'GRID', {'XPATH': 'xIAM'}),
            ('Callables', 'GRID', {'XPATH': 'xCallables'}),
            ('Workflows', 'GRID', {'XPATH': 'xWorkflows'}),
            ('Approvals', 'GRID', {'XPATH': 'xApprovals', 'ROWS': 1}),
            ('Is Encrypted', 'SWITCH'),
            ('Register Repo', 'SWITCH'),
            ('Minimized', 'JSON'),
            ('Maximized', 'JSON'),
            ('Validators', 'GRID', {'XPATH': 'xCallables'}),
            ('Side Effects', 'GRID', {'XPATH': 'xCallables'}),
        ],
        'xMappers': {
            'TEXT': mini_text,
            'JSON': mini_text,
            'GRID': mini_grid,
            'NUMERIC': mini_numeric,
            'SWITCH': mini_switch,
            'ENUM': mini_enum,
            'URI': mini_uri,
        },
        'xTasks': [
            'Milestone',
            'Priority',
        ],
        'xBOW': [
            ('Tasks', 'GRID', {'XPATH': 'xTasks'}),
            ('Parent', 'GRID', {'XPATH': 'xTasks', 'COLLAPSED': True}),
        ],
        'xPeople': [
            ('Alias', 'TEXT', {'LENGTH': 8}),
            ('PID', 'TEXT', {'LENGTH': 20}),
        ],
        'xReleases': [
            'Date Planned',
            'Type'
            'Window Start',
            'Window End',
            'LOB',
            'CRQ',
            'Description',
            'Regulatory Material',
            'Lead',
            ('Approvals', 'GRID', {'XPATH': 'xApprovals', 'ROWS': 1}),
        ],
        'xAITs': [
            ('Alias', 'TEXT', {'LENGTH': 40}),
            ('Application', 'NUMERIC'),
            ('AIT Number', 'NUMERIC'),
        ],
        'xTables': [
            {
                'PATH': '/CORE/REGISTRY/Enumerations',
                'SCHEMA': 'Enumerations',
                'XREF': 'xEnumerations',
            },
            {
                'PATH': '/CORE/REGISTRY/Callables',
                'SCHEMA': 'Callables',
                'XREF': 'xCallables',
            },
            {
                'PATH': '/CORE/REGISTRY/IAM',
                'SCHEMA': 'IAM',
                'XREF': 'xIAM',
            },
            {
                'PATH': '/CORE/REGISTRY/xSchemas',
                'SCHEMA': 'xSchemas',
                'XREF': 'xSchemas',
            },
            {
                'PATH': '/CORE/REGISTRY/Repos',
                'SCHEMA': 'Repos',
                'XREF': 'xRepos',
            },
            {
                'PATH': '/ORG/People',
                'SCHEMA': 'People',
                'XREF': 'xPeople',
            },
            {
                'PATH': '/ORG/BOW',
                'SCHEMA': 'BOW',
                'XREF': 'xBOW',
            },
            {
                'PATH': '/ORG/Funding',
                'SCHEMA': 'Funding',
                'XREF': 'xFunding',
            },
            {
                'PATH': '/ORG/P2P',
                'SCHEMA': 'P2P',
                'XREF': 'xP2P',
            },
            {
                'PATH': '/ORG/Metrics',
                'SCHEMA': 'Metrics',
                'XREF': 'xMetrics',
            },
            {
                'PATH': '/ORG/Bookmarks',
                'SCHEMA': 'Bookmarks',
                'XREF': 'xBookmarks'
            },
            {
                'PATH': '/PLATFORMS/Applications',
                'SCHEMA': 'Applications',
                'XREF': 'xAIT',
            },
            {
                'PATH': '/PLATFORMS/Products',
                'SCHEMA': 'Products',
                'XREF': 'xProducts',
            },
            {
                'PATH': '/PLATFORMS/APLS',
                'SCHEMA': 'APL',
                'XREF': 'xAPL',
            },
            {
                'PATH': '/PLATFORMS/Capabilities',
                'SCHEMA': 'Capabilities',
                'XREF': 'xCapabilities',
            },
            {
                'PATH': '/PLATFORMS/Schedulers',
                'SCHEMA': 'Schedulers',
                'XREF': 'xScheduler',
            },
            {
                'PATH': '/PLATFORMS/Notifications',
                'SCHEMA': 'Schedulers',
                'XREF': 'xScheduler',
            },
            {
                'PATH': '/PLATFORMS/Postman',
                'SCHEMA': 'Schedulers',
                'XREF': 'xMailman',
            },
            {
                'PATH': '/PLATFORMS/Reports',
                'SCHEMA': 'Reports',
                'XREF': 'xReports',
            },
            {
                'PATH': '/PLATFORMS/Translations',
                'SCHEMA': 'Translations',
                'XREF': 'xTranslations',
            },
            {
                'PATH': '/PLATFORMS/EndPoints',
                'SCHEMA': 'API End Points',
                'XREF': 'xAPI',
            },
            {
                'PATH': '/PLATFORMS/Taxonomies',
                'SCHEMA': 'Taxonomy',
                'XREF': 'xTaxonomies'
            },
        ]
    }


main()
