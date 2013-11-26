VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.define :frontend do |frontend_config|

    frontend_config.vm.box = "precise64_base"
    frontend_config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    
    # don't need to forward ports if using private network
    #frontend_config.vm.network :forwarded_port, guest: 9181, host: 9181 # rqdash
    #frontend_config.vm.network :forwarded_port, guest: 9001, host: 9001 # supervisord
    #frontend_config.vm.network :forwarded_port, guest: 8000, host: 8001 # tornado native
    #frontend_config.vm.network :forwarded_port, guest: 80, host: 8100 # tornado through nginx

    #frontend_config.vm.network :public_network, :bridge => 'en0: Wi-Fi (AirPort)'
    
    frontend_config.vm.network :private_network, ip: "192.168.100.10"

    frontend_config.vm.provider :virtualbox do |vb|

    # disabling limits since build takes forever...
    
      #vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
      #vb.customize ["modifyvm", :id, "--ioapic", "on"]
      #vb.customize ["modifyvm", :id, "--memory", "1048"]
      #vb.customize ["modifyvm", :id, "--cpus", "2"]
    end

    ## Frontend currently uses fabric to provision

  end

  config.vm.define :engine do |engine_config|

    engine_config.vm.box = "gridneuro"
    engine_config.vm.box_url = "https://dl.dropboxusercontent.com/u/363467/precise64_neuro.box"
    engine_config.vm.network :forwarded_port, guest: 80, host: 8080

    #engine_config.vm.network :public_network, :bridge => 'en0: Wi-Fi (AirPort)'
    engine_config.vm.network :private_network, ip: "192.168.100.20"
    engine_config.vm.hostname = 'neuro'
    engine_config.vm.synced_folder "../software", "/software"
    engine_config.vm.synced_folder "../data", "/data"
    engine_config.vm.synced_folder "../adhd200", "/adhd200"

    engine_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
      vb.customize ["modifyvm", :id, "--ioapic", "on"]
      vb.customize ["modifyvm", :id, "--memory", "4096"]
      vb.customize ["modifyvm", :id, "--cpus", "4"]
    end

    engine_config.vm.provision :ansible do |ansible|
      ansible.playbook = "common/ops/vagrant-engineserver.yml"
  	  ansible.inventory_path = "common/ops/vagrant-hosts"
    end

  end

  config.vm.define :virtuoso do |virt_config|

    virt_config.vm.box = "precise64_base"
    virt_config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    #virt_config.vm.network :forwarded_port, guest: 8890, host: 8890
    #virt_config.vm.network :public_network, :bridge => 'en0: Wi-Fi (AirPort)'
    virt_config.vm.network :private_network, ip: "192.168.100.30"

    virt_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
      vb.customize ["modifyvm", :id, "--ioapic", "on"]
      vb.customize ["modifyvm", :id, "--memory", "2048"]
      vb.customize ["modifyvm", :id, "--cpus", "2"]
    end

    virt_config.vm.provision :ansible do |ansible|
      #ansible.verbose = 'vvv'
      ansible.playbook = "common/ops/vagrant-virtserver.yml"
      ansible.inventory_path = "common/ops/vagrant-hosts"
    end
  end

  config.vm.define :engine_base do |base_config|

    base_config.vm.box = "precise64_base"
    base_config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    base_config.vm.network :private_network, ip: "192.168.100.40"

    base_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
      vb.customize ["modifyvm", :id, "--ioapic", "on"]
      vb.customize ["modifyvm", :id, "--memory", "2048"]
      vb.customize ["modifyvm", :id, "--cpus", "2"]
    end

    base_config.vm.provision :ansible do |ansible|
    ansible.verbose = 'vvv'
    ansible.playbook = "common/ops/vagrant-baseserver.yml"
    ansible.inventory_path = "common/ops/vagrant-hosts"
    end
  end

end
