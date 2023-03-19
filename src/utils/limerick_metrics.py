import json
from phonemizer.separator import Separator
from phonemizer.backend import FestivalBackend, EspeakBackend
import re

# Usage - use eval for single limerick or eval batch (quicker) for list of limericks
# Each limerick is a list of 5 lines

class LimerickEvaluator:
  def __init__(self, n_jobs = 4):
    self.festival = FestivalBackend('en-us')
    self.espeak = EspeakBackend('en-us', with_stress=True)
    
    self.sep = Separator(phone="-", word=' ', syllable='|')

    self.rhyming_pairs = [(0, 1), (2, 3), (0, 4)]
    self.non_rhyme_pairs = [(0, 2), (0, 3)]
    self.desired_syllables = [8,8,5,5,8]
    self.desired_stress = [3,3,2,2,3]

    self.n_jobs = n_jobs
    
  
  # Main function for EtriCA test.py
  def etrica(self, src_lines, pred_lines, metrics):
    wrong_lines = 0
    limericks = []
    for s, p in zip(src_lines, pred_lines):
      l = p.split(".")
      if len(l) != 5 or len(l[-1]) != 0:
        wrong_lines += 1
      else:
        limericks.append([s] + l[:4])
    
    metrics["limerick-length-error"] = wrong_lines / len(src_lines)
    metrics["limerick-rhyme"] = 0
    metrics["limerick-syllable"] = 0
    metrics["limerick-stress"] = 0

    l_metrics = self.eval_batch(limericks)
    for l in l_metrics:
      for k,v in l.items():
        metrics[k] += v/len(limericks)
        
    
  
  # Get phonemes for list of strings using specified encoder
  def phonemes(self, data, backend="festival"):
    if backend=="festival":
      return self.festival.phonemize(data, separator=self.sep, strip=True, njobs = self.n_jobs)
    if backend=="espeak":
      return self.espeak.phonemize(data, separator=self.sep, strip=True, njobs = self.n_jobs)
    
  # Evaluate single limerick
  def eval(self, limerick):
    phones_festival = self.phonemes(limerick, "festival")
    phones_espeak = self.phonemes(limerick, "espeak")

    return self.metric(phones_festival, phones_espeak)

  # Evaluate list of limericks
  def eval_batch(self, limericks):
    n = len(limericks)
    flat_list = [item for sublist in limericks for item in sublist]
    phones_festival = self.phonemes(flat_list, "festival")
    phones_espeak = self.phonemes(flat_list, "espeak")

    return [self.metric(phones_festival[i*5:(i+1)*5], phones_espeak[i*5:(i+1)*5]) for i in range(n)]

  # Combined error metric of limerick
  # TODO: Tune ratio of errors
  def metric(self, phones_festival, phones_espeak):
    syl_err = self.syllable_error_metric(phones_festival)
    rhyme_err = self.rhyming_error_metric(phones_festival)
    stress_err = self.stress_error_metric(phones_espeak)

    return {
      "limerick-rhyme": rhyme_err,
      "limerick-syllable": syl_err,
      "limerick-stress": stress_err
    }

  # Calculate how close the line lengths (in syllables) is to desired lengths
  # Uses festival encoding for syllable breaks
  def syllable_error_metric(self, phones):
    syllable_count = [len(re.split(' |\|', s)) for s in phones]

    error = sum([abs(x-y) for x,y in zip(syllable_count, self.desired_syllables)])
    return error

  # Calculate how many rhyming pairs and non-rhyme pairs are correct
  def rhyming_error_metric(self, phones):
    last_syllables = [re.split(' |\|', s)[-1] for s in phones]

    rhymes = sum([not self.check_rhyme(last_syllables[x], last_syllables[y]) for x,y in self.rhyming_pairs])
    not_rhymes = sum([self.check_rhyme(last_syllables[x], last_syllables[y]) for x,y in self.non_rhyme_pairs])

    return rhymes + not_rhymes

  # Check if two pairs of lines rhyme
  def check_rhyme(self, phone1, phone2):
    p1 = phone1.split("-")
    p2 = phone2.split("-")

    if len(p1) < len(p2):
      return p1[1:] == p2[len(p2)-len(p1)+1:]
    else:
      return p1[len(p1)-len(p2)+1:] == p2[1:]
  
  # Calculate how close lines (in number of stressed syllables) are to desired
  def stress_error_metric(self, phones):
    stress_count = [s.count("\u02C8") for s in phones]

    error = sum([abs(x-y) for x,y in zip(stress_count, self.desired_stress)])
    return error

