# Inner Source License Clauses

Key:
{} - Variables
[] - Options 

## Definitions

- License
- Licensor - {Copyright holde}
- {Copyright holder}
- {Author} - Creator of the code
- Original Work
- Derivative Work - Work derived from the original InnerSource code
- ReDistribution - Redistribution of the derivative or original work
- {Boundary} - Boundary definition
- Inner Source Code
- Contribution
- Contributor
- Licensee
- {Subsidaries}
- {Partners}
- {Vendors}
- {Authorized Vendors}
- {Inner Source Authorizing body}


## Copyright Holder
1. Organization owning Inner Source product

## Point of Agreement
1. Upon download of source code (click through license)

## Scope 
Options
[
1. Source code 
2. DevOps code 
3. Data
5. Documentation
6. SDLC artifacts
]

*comments*
1. Issues might also need to be included - schlomo

## Allowed Distribution 
Clause Options: [
1. Within Organization, but not {Subsidaries} or {Vendors} 
2. Within Organization and {Subsidaries}, but not with {Vendors}
3. Within Organization, {Subsidaries} and {Authorized Vendors} 
]
*Comments*
- Potential "data seperation walls" in org <- Peter
   - > A) think thought other seperatation/boundary concerns.
   - > consider mergers and aquasitions - Schlomo
       -> license grants central body power to grant problamatic cases
       -> Need an body to authorize a body 
       
## Inner Source Authorizing Body
Clause Options [
1. OSPO
2. Inner Source Committee
3. {named entity}
]

*Comments*
1. Can be a license/contract governing body
2. can be a inner source committee
3. Can be a vriable in the generator - Chamindra
  
## Territory
Clause Options (multiple options):[
1. US territories
2. Europe/EU
3. UK
4. ...
]
   
*Comments*
- US territories <- export restrictions for source code (e.g. encryption algorithms, cloud-data) <- Peter
- GPL liability <- can have issues with enforcement in German law <- schlomo
  
## type of use - DB/Schlomo
1. only for business use of company (not for general use)
   
## License Grant
1. Grant to use, analyze and modify source code
  - Term
  - Exceptions

## Attribution
Clause Options: [
1. No Attribution (no retention of material)
2. Attribution to Copyright holder (retention of material) 
3. Attribution to Project (retention of material) <- clearly name the authors - Schlomo
]

## Confidentiality
                                                     
* Comments *
Types of sensative information                                                    
1. No sensative configuration to be included in derivative work
2. e.g training sets (e.g data)
3. Algorithm

## ReDistribution
Clause Options: [
1. No redistribution
2. Redsitribution allowed 
3. Redistrubution allowed with central registration
]

*Comments*
1. No redistribution would essential mean it is not inner source so would remove this unless we expcitly say it is only back to the source

## Derivative works
Clause Options: [                                                   
1. Retains License (Copyleft)
2. Weak Copyleft
3. Permissive
]

*Comments*
1. GPL type copyleft <- Copy left was important for DB and was the part convinced teams to inner source software - schlomo
   - Attribution does not prevent improvement 
2. Weak copyleft might not be necessary in the context of inner source - Chamindra
                   
## Termination
Clause Options: [
1. Right to revoke license on violation
2. 30 day termination clause
]

## Warrenty
Clause Options: [
1. 30 day Warrenty - https://patterns.innersourcecommons.org/p/30-day-warranty
2. no Warrenty / As-Is
3. Security Fixes
4. Bug Fixes
]

## Liability and Indemnity
1. No Liability

*Comments*
1. Warrenty, Liability and other terms might get invalidated by the law of the land (e.g germany) - Cornelius

## LLM Access
1. Will LLM (Large Language Models) tools like ChatGPT be given access 
Clause Option
1. No Access 
2. Internal Only 
3. Internal Only with Attribution

*Comments*
1. LLM access can become a significant element of InnerSource license - Chamindra

