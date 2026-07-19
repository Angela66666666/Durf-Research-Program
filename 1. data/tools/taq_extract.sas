options mprint mlogic symbolgen;

/* Change this to your WRDS output path */
libname out "/scratch/nyu/gzheng";

/* September through December 2024 */
%let start_dt = '01SEP2024'd;
%let end_dt   = '31DEC2024'd;

%let outdsn = out.nbbo_vgrd_etfs;

/* ETF list */
%let tickers = "VOX","VCR","VDC","VDE","VFH","VHT","VIS","VGT","VAW","VNQ","VPU";

/* Start fresh */
proc datasets lib=out nolist;
  delete nbbo_vgrd_etfs;
quit;

/* Build daily table suffixes: YYYYMMDD */
data _dates;
  format dt yymmddn8.;
  do dt = &start_dt to &end_dt;
    ymd = put(dt, yymmddn8.);
    output;
  end;
run;

data _null_;
  set _dates end=eof;
  call symputx(cats('d', _n_), ymd);
  if eof then call symputx('ndays', _n_);
run;

%macro pull_nbbo_range;
  %local i ymd indsn;

  %do i = 1 %to &ndays;
    %let ymd = &&d&i;
    %let indsn = taqmsec.complete_nbbo_&ymd;

    %put NOTE: Processing &indsn;

    %if %sysfunc(exist(&indsn)) %then %do;

      data _day(keep=date time_m sym_root best_bid best_ask);
        set &indsn(keep=sym_root date time_m best_bid best_ask);
        where sym_root in (&tickers);
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

%pull_nbbo_range;
