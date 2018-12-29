/* Copyright (C) 2013, 2014, 2018  Olga Yakovleva <yakovleva.o.v@gmail.com> */

/* This program is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU Lesser General Public License as published by */
/* the Free Software Foundation, either version 2.1 of the License, or */
/* (at your option) any later version. */

/* This program is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU Lesser General Public License for more details. */

/* You should have received a copy of the GNU Lesser General Public License */
/* along with this program.  If not, see <http://www.gnu.org/licenses/>. */

#include "core/str.hpp"
#include "core/path.hpp"
#include "core/config.hpp"
#include "core/voice.hpp"
#include "core/hts_engine_impl.hpp"

namespace RHVoice
{
  hts_engine_impl::hts_engine_impl(const std::string& impl_name,const voice_info& info_):
    info(info_),
    data_path(info_.get_data_path()),
    quality(quality_none),
    beta("beta",0.4,-0.8,0.8),
    gain("gain",1.0,0.5,2.0),
    input(0),
    output(0),
    rate(1.0),
    name(impl_name)
  {
    config cfg2;
    cfg2.register_setting(beta);
    cfg2.register_setting(gain);
    cfg2.load(path::join(data_path,"voice.params"));
  }

  void hts_engine_impl::synthesize()
  {
    if(input->lbegin()!=input->lend())
      do_synthesize();
    if(!output->is_stopped())
      output->finish();
  }

  void hts_engine_impl::reset()
  {
    if(input->lbegin()!=input->lend())
      do_reset();
    output=0;
    input=0;
    rate=1.0;
  }

  void hts_engine_impl::load_configs()
  {
    config cfg2;
    cfg2.register_setting(beta);
    cfg2.register_setting(gain);
    cfg2.load(path::join(data_path,"voice.params"));
  }

  hts_engine_impl::pointer hts_engine_impl::create(quality_t q) const
  {
    pointer p=do_create();
    p->set_quality(q);
    p->load_configs();
    p->do_initialize();
    return p;
  }

  void hts_engine_impl::on_new_sample(short sample)
  {
    if(output->is_stopped())
      {
        do_stop();
        return;
      }
    double s=(sample/32768.0);
    try
      {
        output->process(&s,1);
      }
    catch(...)
      {
        output->stop();
      }
    if(output->is_stopped())
      do_stop();
  }

  sample_rate_t hts_engine_impl::get_sample_rate_for_quality(quality_t q) const
  {
    if(info.get_format()==3)
      return sample_rate_24k;
    switch(q)
      {
      case quality_min:
        return sample_rate_16k;
      default:
        return sample_rate_24k;
}
}

  void hts_engine_impl::set_quality(quality_t q)
  {
    quality=q;
    if(info.get_format()==3)
      model_path=data_path;
    else
      model_path=path::join(data_path,str::to_string(get_sample_rate_for_quality(q)));
}
}
