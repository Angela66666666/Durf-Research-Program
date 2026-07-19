/*------------------------------------------------------------
  WRDS TAQ NBBO (daily tables) → month extract for TSLA
  Tables look like: TAQMSEC.COMPLETE_NBBO_YYYYMMDD
------------------------------------------------------------*/

options mprint mlogic symbolgen;

/* Where you want the month extract to live */
libname out "/scratch/nyu/gzheng";   /* change to your WRDS home/project path */

/* Month bounds */
%let start_dt = '01DEC2025'd;
%let end_dt   = '31DEC2025'd;
%let SYM      = 'TSLA'
/* Output table name */
%let outdsn   = out.nbbo_tsla_2025m12;

/* Start fresh */
proc datasets lib=out nolist;
  delete nbbo_tsla_2025m12;
quit;

/* Build a list of YYYYMMDD strings for each day in the month */
data _dates;
  format dt yymmddn8.;
  do dt = &start_dt to &end_dt;
    ymd = put(dt, yymmddn8.);  /* e.g. 20251201 */
    output;
  end;
run;

/* Put the list into macro vars d1-d31, with &ndays */
data _null_;
  set _dates end=eof;
  call symputx(cats('d',_n_), ymd);
  if eof then call symputx('ndays', _n_);
run;

/* Loop days: read each daily table, filter TSLA, append */
%macro pull_nbbo_month;
  %local i ymd indsn;

  %do i = 1 %to &ndays;
    %let ymd = &&d&i;
    %let indsn = taqmsec.complete_nbbo_&ymd;

    %put NOTE: Processing &indsn;

    /* If some day is missing, skip gracefully */
    %if %sysfunc(exist(&indsn)) %then %do;

	  data _day(keep=date time_m best_bid best_ask Best_BidSizeShares Best_AskSizeShares);
  		set &indsn(keep=sym_root date time_m best_bid best_ask Best_BidSizeShares Best_AskSizeShares);
        where sym_root = &SYM;
      run;

      proc append base=&outdsn data=_day force;
      run;

      proc datasets lib=work nolist;
        delete _day;
      quit;

    %end;
    %else %do;
      %put WARNING: Dataset &indsn does not exist. Skipping.;
    %end;

  %end;
%mend;

%pull_nbbo_month;
