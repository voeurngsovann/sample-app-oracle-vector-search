create user dev identified by Welcome1;
grant create session, db_developer_role, create mining model,dba to dev;

create or replace directory model_dir as '/u01/models';
grant read, write on directory model_dir to dev;

connect dev/Welcome1@AIDBPDB1

#download model 
#https://adwc4pm.objectstorage.us-ashburn-1.oci.customer-oci.com/p/fU1V-voY2VBhhqMPjhCC57Up77ROK9u6GN_j3-uGi_EzIdHm9XDn-RfnZS5bV0cN/n/adwc4pm/b/OML-ai-models/o/Oracle%20Machine%20Learning%20AI%20models.htm
begin
  dbms_vector.drop_onnx_model (
    model_name => 'ALL_MINILM_L12_V2',
    force => true);

  dbms_vector.load_onnx_model (
    directory  => 'model_dir',
    file_name  => 'all_MiniLM_L12_v2.onnx',
    model_name => 'ALL_MINILM_L12_V2');
end;
/


column model_name format a30
column algorithm format a10
column mining_function format a15

select model_name, algorithm, mining_function
from   user_mining_models where  model_name = 'ALL_MINILM_L12_V2';


CREATE SEQUENCE dev.SEQ_QUESTION_CACHE_ID 
START WITH 1 
INCREMENT BY 1 
NOCACHE 
NOCYCLE;

CREATE TABLE dev.QUESTION_CACHE (
    id              NUMBER          DEFAULT dev.SEQ_QUESTION_CACHE_ID.NEXTVAL
                                    NOT NULL
                                    CONSTRAINT PK_QUESTION_CACHE_ID PRIMARY KEY,
    user_id         NUMBER          NOT NULL,
    question        VARCHAR2(4000)  NOT NULL,
    answer          CLOB            NOT NULL,
    response_time   NUMBER,
    created_at      TIMESTAMP       DEFAULT SYSTIMESTAMP,
    CONSTRAINT FK_QUESTION_CACHE_USER FOREIGN KEY (user_id)
        REFERENCES dev.VS_APP_USERS(id) ON DELETE CASCADE
);



CREATE INDEX dev.IDX_QUESTION_CACHE_USER_Q ON dev.QUESTION_CACHE(user_id, question);